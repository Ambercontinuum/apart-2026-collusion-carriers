"""One ephemeral Modal compatibility request, never an experimental episode."""

import hashlib
import json
from pathlib import Path
import sys

import modal

MODEL = "Qwen/Qwen3-4B-Instruct-2507"
app = modal.App("apart-single-call-compatibility")
image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "vllm==0.11.0", "transformers==4.57.1", "huggingface-hub==0.35.3", "openai==2.3.0"
)


@app.function(image=image, gpu="L4", timeout=600, retries=0, max_containers=1)
def probe(request_text):
    import subprocess
    import tempfile
    import time
    import urllib.error
    import urllib.request

    from huggingface_hub import HfApi

    revision = HfApi().model_info(MODEL).sha
    command = [
        "python", "-m", "vllm.entrypoints.openai.api_server",
        "--model", MODEL, "--revision", revision, "--tokenizer-revision", revision,
        "--host", "127.0.0.1", "--port", "8000", "--max-model-len", "2048",
        "--max-num-seqs", "1", "--gpu-memory-utilization", "0.85",
        "--enforce-eager", "--enable-auto-tool-choice", "--tool-call-parser", "hermes",
    ]
    started = time.monotonic()
    with tempfile.TemporaryFile() as log:
        server = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        try:
            while time.monotonic() - started < 480:
                if server.poll() is not None:
                    raise RuntimeError("vLLM exited before readiness; no inference request sent")
                try:
                    with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2):
                        break
                except (OSError, urllib.error.URLError):
                    time.sleep(2)  # Readiness only, never inference retries.
            else:
                raise TimeoutError("server readiness timeout; no inference request sent")
            request = urllib.request.Request(
                "http://127.0.0.1:8000/v1/chat/completions",
                data=request_text.encode("utf-8"), headers={"Content-Type": "application/json"},
            )
            try:
                with urllib.request.urlopen(request, timeout=75) as response:
                    status, raw = response.status, response.read().decode("utf-8")
            except urllib.error.HTTPError as error:
                status, raw = error.code, error.read().decode("utf-8")
            return {"http_status": status, "raw_response": raw, "model_revision": revision,
                    "inference_attempts": 1, "elapsed_seconds": time.monotonic() - started,
                    "server_command": command}
        finally:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()


@app.local_entrypoint()
def main():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "colosseum"))
    from experiments.collusion.apart_2026.provider import LiveProvider, ProviderConfig

    out = root / "evidence/live-smoke/modal-single-call-20261024"
    config = ProviderConfig(model=MODEL, temperature=0.0, max_tokens=64)
    provider = LiveProvider(config, lambda _: None)
    request_text = provider.request_text(
        [{"role": "user", "content": "Call compatibility_ping with value 1. Do not add text."}],
        [{"type": "function", "function": {
            "name": "compatibility_ping", "description": "A compatibility check; no side effects.",
            "parameters": {"type": "object", "properties": {"value": {"type": "integer", "enum": [1]}},
                           "required": ["value"], "additionalProperties": False},
        }}],
    )
    with (out / "request.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(request_text)
    result = probe.remote(request_text)
    with (out / "response.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2)
    live = LiveProvider(config, lambda _: result["raw_response"])
    parsed = live.complete(messages=[], tools=[], agent="compatibility", phase="smoke", slot=1)
    summary = {
        "research_result": False, "experimental_episodes": 0,
        "model": MODEL, "model_revision": result["model_revision"], "gpu": "L4",
        "modal_client_version": "1.2.2", "vllm_version": "0.11.0",
        "inference_attempts": result["inference_attempts"], "http_status": result["http_status"],
        "parsed_response": parsed,
        "expected_call": parsed["tool_calls"] == [{"name": "compatibility_ping", "arguments": {"value": 1}}],
        "request_sha256": hashlib.sha256(request_text.encode()).hexdigest(),
        "response_sha256": hashlib.sha256(result["raw_response"].encode()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    with (out / "summary.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(summary, stream, indent=2)
    print(json.dumps({key: summary[key] for key in ("http_status", "expected_call", "inference_attempts")}))
