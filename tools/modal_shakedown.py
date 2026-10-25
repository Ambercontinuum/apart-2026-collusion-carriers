"""Authorized exploratory B0/B2 pair; fail on first invalid turn, no retries."""

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

import modal

MODEL = "Qwen/Qwen3-4B-Instruct-2507"
REVISION = "cdbee75f17c01a7cc42f958dc650907174af0554"
IMAGE_ID = "im-ed45DntZxJyX86mmRWdWKq"
app = modal.App("apart-b0-b2-shakedown")


@app.cls(image=modal.Image.from_id(IMAGE_ID), gpu="L4", timeout=900,
         retries=0, max_containers=1, scaledown_window=30)
class Server:
    request_limit: int = modal.parameter(default=40)

    @modal.enter()
    def start(self):
        import subprocess
        import time
        import urllib.request

        from transformers import AutoTokenizer

        self.calls = 0
        if not 1 <= self.request_limit <= 300:
            raise ValueError("request limit outside authorized bounded runner range")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
        self.log = tempfile.TemporaryFile()
        self.server = subprocess.Popen([
            "python", "-m", "vllm.entrypoints.openai.api_server",
            "--model", MODEL, "--revision", REVISION, "--tokenizer-revision", REVISION,
            "--host", "127.0.0.1", "--port", "8000", "--max-model-len", "8192",
            "--max-num-seqs", "1", "--gpu-memory-utilization", "0.85", "--enforce-eager",
            "--enable-auto-tool-choice", "--tool-call-parser", "hermes",
        ], stdout=self.log, stderr=self.log)
        started = time.monotonic()
        while time.monotonic() - started < 480:
            if self.server.poll() is not None:
                self.log.seek(0)
                raise RuntimeError(self.log.read().decode(errors="replace")[-6000:])
            try:
                with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2):
                    return
            except OSError:
                time.sleep(2)
        self.stop_server()
        raise TimeoutError("server not ready; no inference")

    @modal.method()
    def request(self, text):
        import urllib.error
        import urllib.request

        payload = json.loads(text)
        if self.calls >= self.request_limit or payload["max_tokens"] > 256 or payload["model"] != MODEL:
            raise ValueError("shakedown request budget/configuration exceeded")
        if payload["tool_choice"] != "required":
            raise ValueError("required tool choice only")
        tokens = len(self.tokenizer.apply_chat_template(
            payload["messages"], tools=payload["tools"], tokenize=True, add_generation_prompt=True,
        ))
        if tokens + payload["max_tokens"] > 8192:
            raise ValueError("tokenized context exceeds reserved output budget; no request sent")
        self.calls += 1
        request = urllib.request.Request(
            "http://127.0.0.1:8000/v1/chat/completions", data=text.encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                status, raw = response.status, response.read().decode()
        except urllib.error.HTTPError as error:
            status, raw = error.code, error.read().decode()
        return {"raw": raw, "http_status": status, "preflight_prompt_tokens": tokens,
                "actual_request_index": self.calls, "model": MODEL, "revision": REVISION,
                "image": IMAGE_ID, "vllm": "0.11.0"}

    def stop_server(self):
        if hasattr(self, "server") and self.server.poll() is None:
            self.server.terminate()
            try:
                self.server.wait(timeout=10)
            except Exception:
                self.server.kill()
                self.server.wait()

    @modal.method()
    def close(self):
        self.stop_server()
        return {"inference_requests": self.calls, "server_stopped": True}

    @modal.exit()
    def exit(self):
        self.stop_server()


@app.local_entrypoint()
def main():
    root = Path(__file__).resolve().parents[1]
    # Same Python 3.12; read existing locked task dependencies without installing
    # into or altering the project's environment.
    sys.path.append(str(root / ".venv/Lib/site-packages"))
    sys.path.insert(0, str(root / "colosseum"))
    from experiments.collusion.apart_2026.preview import _finite_wire
    from experiments.collusion.apart_2026.provider import MODAL_STOP_CONTRACT, LiveProvider, ProviderConfig
    from experiments.collusion.apart_2026.runner import EpisodeRunner, make_environment

    output = root / "evidence/shakedown/b0-b2-seed1-20261024"
    output.mkdir(parents=True, exist_ok=False)
    worker = Server()
    transport_events = []
    episodes = []
    cwd = Path.cwd()

    def save(path, data):
        path.write_text(json.dumps(_finite_wire(data), indent=2, sort_keys=True),
                        encoding="utf-8", newline="\n")

    def transport(text):
        if len(transport_events) >= 40:
            raise RuntimeError("total request cap")
        # Persist intended request before the remote call, including uncertain
        # transport failures. Never repeat this call after an exception.
        event = {"request_text": text, "request_sha256": hashlib.sha256(text.encode()).hexdigest()}
        transport_events.append(event)
        save(output / "transport.json", transport_events)
        result = worker.request.remote(text)
        if any(result[key] != MODAL_STOP_CONTRACT[key]
               for key in ("model", "revision", "image", "vllm")):
            raise RuntimeError("route identity mismatch")
        event.update(result)
        save(output / "transport.json", transport_events)
        return result["raw"]

    def capture(runner, arm):
        data = {"condition": arm, "seed": 1, "failures": runner.failures,
                "provider_inputs": runner.provider_inputs,
                "provider_responses": runner.provider_responses,
                "provider_exchanges": runner.provider.exchanges,
                "tool_results": runner.tool_results, "host_events": runner.stage.research_events(),
                "final_summary": runner.env.get_final_summary(),
                "native_config": runner.env.full_config,
                "coalition": runner.stage.coalition,
                "complete": not runner.failures and len(runner.tool_results) == 20}
        save(output / (arm + ".json"), data)
        return data

    stopped_early = False
    shutdown = None
    error = None
    try:
        for arm in ("B0", "B2"):
            with tempfile.TemporaryDirectory() as temporary:
                try:
                    os.chdir(temporary)
                    config = ProviderConfig(MODEL, temperature=0.0, max_tokens=256, seed=1)
                    provider = LiveProvider(config, transport, completion_contract=MODAL_STOP_CONTRACT)
                    runner = EpisodeRunner(make_environment(1), condition=arm, episode_seed=1, provider=provider)
                    for phase, slots in (("preview", range(1, 5)), ("execution", (1,))):
                        if phase == "execution":
                            try:
                                runner.stage.release()
                            except Exception as exc:
                                runner.failures.append({"phase": "barrier", "error_type": type(exc).__name__})
                                stopped_early = True
                                break
                        for slot in slots:
                            for agent in runner.stage.agents:
                                runner._turn(agent, phase, slot)
                                capture(runner, arm)
                                print(json.dumps({"arm": arm, "phase": phase, "slot": slot,
                                                  "agent": agent, "requests": len(transport_events),
                                                  "invalid": bool(runner.failures)}), flush=True)
                                if runner.failures:
                                    stopped_early = True
                                    break
                            if stopped_early:
                                break
                        if stopped_early:
                            break
                    episodes.append(capture(runner, arm))
                finally:
                    os.chdir(cwd)
            if stopped_early:
                break
    except Exception as exc:
        error = {"error_type": type(exc).__name__}
        stopped_early = True
    finally:
        os.chdir(cwd)
        try:
            shutdown = worker.close.remote()
        except Exception as exc:
            shutdown = {"error_type": type(exc).__name__, "verify_app_shutdown": True}
        result = {"scope": "exploratory shakedown, not registered pilot", "seed": 1,
                  "planned_conditions": ["B0", "B2"], "completed_conditions": [
                      data["condition"] for data in episodes if data["complete"]],
                  "attempted_conditions": [data["condition"] for data in episodes],
                  "requests_attempted": len(transport_events), "request_cap": 40,
                  "max_output_tokens": 256, "stopped_on_failure": stopped_early,
                  "error": error, "shutdown": shutdown, "completion_contract": MODAL_STOP_CONTRACT,
                  "max_model_len": 8192, "gate0_passed": False,
                  "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [
                      Path(__file__), root / "colosseum/experiments/collusion/apart_2026/provider.py",
                      root / "colosseum/experiments/collusion/apart_2026/runner.py"]},
                  "output_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in output.iterdir() if p.is_file()}}
        save(output / "summary.json", result)
        print(json.dumps(result), flush=True)
