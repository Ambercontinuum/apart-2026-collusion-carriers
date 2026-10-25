"""Run supplied ungated P seed1 via pinned ephemeral Modal transport."""

import asyncio
import copy
import hashlib
import importlib.util
import json
import os
import queue
from pathlib import Path
import sys
import tempfile

from modal_shakedown import IMAGE_ID, MODEL, REVISION, Server, app


@app.local_entrypoint()
def positive_control():
    root = Path(__file__).resolve().parents[1]
    parent = root.parent
    sys.path.append(str(root / ".venv/Lib/site-packages"))
    sys.path.insert(0, str(parent / "util"))
    sys.path.insert(0, str(parent / "colosseum"))
    import yaml
    from experiments.collusion import run as upstream
    from experiments.common import providers
    from llm_server.clients.together_client import TogetherClient, _convert_tools
    from poseidon_compute import llm_config

    # No dotenv or key loading. The native agent loop receives a transport-only
    # client; no native source, prompt, tool or scoring implementation is patched.
    llm_config._load = lambda: None
    providers.resolve_model = lambda requested: requested
    upstream.get_model_name = lambda provider, config: MODEL
    spec = importlib.util.spec_from_file_location(
        "apart_strict_p_wire", root / "colosseum/experiments/collusion/apart_2026/provider.py")
    wire = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = wire
    spec.loader.exec_module(wire)
    output = root / "evidence/calibration/p-qwen3-4b-seed1-20261024/attempt3"
    output.mkdir(parents=True, exist_ok=False)
    original = parent / "colosseum/experiments/collusion/configs/hackathon_positive_control.yaml"
    cfg = yaml.safe_load(original.read_text())
    cfg["llm_models"][0]["llm"]["openrouter"]["model"] = MODEL
    cfg["experiment"]["output_dir"] = str(output / "native")
    (output / "config.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8", newline="\n")
    (output / "supplied-config.yaml").write_bytes(original.read_bytes())
    # Reserve one budget slot for the stopped attempt's unresolved local handoff.
    server = Server(request_limit=35, output_limit=1500, required_tools=False)
    events = []
    halted = None
    handoff = queue.Queue()

    def remote_on_main(text):
        reply = queue.Queue(maxsize=1)
        handoff.put((text, reply))
        result = reply.get()
        if isinstance(result, BaseException):
            raise result
        return result

    def save():
        (output / "transport.json").write_text(json.dumps(events, indent=2), encoding="utf-8", newline="\n")

    class Client(TogetherClient):
        def __init__(self, actor):
            self.actor = actor  # Deliberately bypass TogetherClient's dotenv/key initialization.

        def generate_response(self, input, params):
            nonlocal halted
            if halted or len(events) >= 35:
                raise RuntimeError("P transport halted or budget exhausted; no further requests")
            maximum = params.get("max_completion_tokens") or params.get("max_output_tokens") or params.get("max_tokens")
            if maximum != 1500 or params.get("temperature") != 0.7 or params.get("model") != MODEL:
                halted = "configuration mismatch"
                raise RuntimeError(halted)
            payload = {"model": MODEL, "messages": copy.deepcopy(input),
                       "temperature": 0.7, "max_tokens": 1500}
            tools = _convert_tools(params.get("tools"))
            if tools:
                payload["tools"] = tools
            text = json.dumps(payload, allow_nan=False, separators=(",", ":"))
            event = {"agent": self.actor, "request_text": text,
                     "request_sha256": hashlib.sha256(text.encode()).hexdigest()}
            events.append(event)
            save()
            try:
                result = remote_on_main(text)
                event.update(result)
                save()
                if result["http_status"] != 200 or any(result[k] != expected for k, expected in {
                    "model": MODEL, "revision": REVISION, "image": IMAGE_ID, "vllm": "0.11.0"}.items()):
                    raise ValueError("HTTP or route mismatch")
                body = wire.strict_loads(result["raw"])
                if body.get("model") != MODEL or len(body.get("choices", [])) != 1:
                    raise ValueError("invalid model or choices")
                choice = body["choices"][0]
                if choice.get("finish_reason") not in ("stop", "tool_calls"):
                    raise ValueError("incomplete/unknown finish status")
                message = choice.get("message")
                if not isinstance(message, dict):
                    raise ValueError("missing message")
                # P permits multiple native tool calls and assistant text; validate
                # arguments before inherited processing can silently repair JSON.
                calls = message.get("tool_calls") or []
                if not isinstance(calls, list):
                    raise ValueError("invalid tool batch")
                for call in calls:
                    fn = call.get("function", {})
                    if call.get("type") != "function" or not isinstance(fn.get("name"), str):
                        raise ValueError("invalid function call")
                    if not isinstance(fn.get("arguments"), str) or not isinstance(wire.strict_loads(fn["arguments"]), dict):
                        raise ValueError("invalid tool arguments")
                return body, self._extract_message_content(body)
            except Exception as exc:
                halted = type(exc).__name__
                event["failure"] = halted
                save()
                raise

    upstream.get_client_instance = lambda config, agent_name=None, **kwargs: Client(agent_name)
    upstream._configure_experiment_logging(output, verbose=False)
    result = None
    failure = None
    shutdown = None
    cwd = Path.cwd()
    try:
        with tempfile.TemporaryDirectory() as temporary:
            try:
                os.chdir(temporary)
                native_run = upstream._run_single(
                    base_cfg=cfg, model_label="q", model_llm_cfg=cfg["llm_models"][0]["llm"],
                    sweep_name="p", topology="complete", num_agents=4,
                    colluder_count=2, secret_channel_enabled=True, prompt_variant="simple",
                    seed=1, out_dir=Path(temporary) / "p",
                )
                # Native agents use their own thread pool. Keep Modal's blocking
                # SDK on this entrypoint thread, avoiding nested bridge calls.
                from concurrent.futures import ThreadPoolExecutor

                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(asyncio.run, native_run)
                    while not future.done():
                        try:
                            text, reply = handoff.get(timeout=0.1)
                        except queue.Empty:
                            continue
                        try:
                            reply.put(server.request.remote(text))
                        except Exception as exc:
                            reply.put(exc)
                    result = future.result()
            finally:
                import zipfile

                native = Path(temporary) / "p"
                if native.exists():
                    with zipfile.ZipFile(output / "native-results.zip", "x", zipfile.ZIP_DEFLATED) as archive:
                        for artifact in native.rglob("*"):
                            if artifact.is_file():
                                archive.write(artifact, artifact.relative_to(native).as_posix())
                os.chdir(cwd)
    except Exception as exc:
        failure = type(exc).__name__
    finally:
        try:
            shutdown = server.close.remote() if events else {"inference_requests": 0, "server_started": False}
        except Exception as exc:
            shutdown = {"error_type": type(exc).__name__}
        save()
        summary = {"scope": "supplied P ungated calibration, not D1 matched contrast",
                   "seed": 1, "requests_attempted": len(events), "request_cap": 35,
                   "previous_unresolved_local_handoff_budget_reserve": 1,
                   "failure": failure, "transport_halted": halted, "result": result,
                   "shutdown": shutdown, "SERAPH_mediation": False,
                   "source_sha256": {str(p.relative_to(parent)): hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in [Path(__file__), parent / "colosseum/experiments/collusion/run.py",
                                               parent / "colosseum/experiments/collusion/metrics.py",
                                               parent / "colosseum/experiments/collusion/prompts.py", original]},
                   "limitations": "P differs in graph/channel/temperature/history; reward advantage alone does not prove causal coordination. Native loop preserved; strict transport validates before parser fallback."}
        (output / "summary.json").write_text(json.dumps(summary, indent=2, default=str),
                                               encoding="utf-8", newline="\n")
        print(json.dumps(summary, default=str), flush=True)
