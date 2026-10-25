"""Frozen as-built five-arm exploratory grid; no tuning or replacement trials."""

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

from modal_shakedown import Server, app


@app.local_entrypoint()
def grid():
    root = Path(__file__).resolve().parents[1]
    sys.path.append(str(root / ".venv/Lib/site-packages"))
    sys.path.insert(0, str(root / "colosseum"))
    from experiments.collusion.apart_2026.preview import _finite_wire
    from experiments.collusion.apart_2026.provider import MODAL_STOP_CONTRACT, LiveProvider, ProviderConfig
    from experiments.collusion.apart_2026.runner import EpisodeRunner, make_environment
    from experiments.collusion.apart_2026.seraph_bridge import load_public_seraph

    seraph_root = root / ".runtime/SERAPH-1.0"
    load_public_seraph(seraph_root)  # Validate source before ANY inference.
    output = root / "evidence/exploratory-grid/freeze-20261024"
    output.mkdir(parents=True, exist_ok=False)
    cells = [(arm, seed) for arm in ("B0", "B1", "B2", "B2-S", "G2") for seed in (1, 2, 3)]
    worker = Server(request_limit=300)
    events = []
    episodes = []
    fatal = None
    active = None
    cwd = Path.cwd()

    def save(path, value):
        path.write_text(json.dumps(_finite_wire(value), indent=2, sort_keys=True),
                        encoding="utf-8", newline="\n")

    package = root / "colosseum/experiments/collusion/apart_2026"
    sources = [Path(__file__), root / "tools/modal_shakedown.py",
               root / "docs/protocol/EXPLORATORY_FREEZE_20261024.md", *package.glob("*.py")]
    freeze = {"scope": "live exploratory as-built grid; NOT full six-condition registered pilot",
              "planned_cells": cells, "P": "not run; not integrated",
              "request_cap": 300, "max_output_tokens": 256, "temperature": 0.0,
              "generation_seed": "native seed", "max_model_len": 8192,
              "completion_contract": MODAL_STOP_CONTRACT,
              "source_sha256": {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sources}, "gate0_passed": False,
              "G2_scope": "certified canonical emission; assignment permit component not integrated"}
    save(output / "freeze.json", freeze)

    def transport(text):
        nonlocal fatal
        if fatal:
            raise RuntimeError("transport halted; no further wire request")
        if len(events) >= 300:
            fatal = "request cap"
            raise RuntimeError(fatal)
        event = {"cell": active, "request_text": text,
                 "request_sha256": hashlib.sha256(text.encode()).hexdigest()}
        events.append(event)
        save(output / "transport.json", events)
        try:
            result = worker.request.remote(text)
            event.update(result)
            save(output / "transport.json", events)
            if any(result[key] != MODAL_STOP_CONTRACT[key]
                   for key in ("model", "revision", "image", "vllm")):
                raise RuntimeError("route identity mismatch")
            if result["http_status"] != 200:
                raise RuntimeError("HTTP failure; abort remaining grid")
            return result["raw"]
        except Exception as exc:
            fatal = type(exc).__name__
            event["transport_error"] = fatal
            save(output / "transport.json", events)
            raise

    shutdown = None
    try:
        for arm, seed in cells:
            active = {"condition": arm, "seed": seed}
            start = len(events)
            with tempfile.TemporaryDirectory() as temporary:
                try:
                    os.chdir(temporary)
                    provider = LiveProvider(
                        ProviderConfig(MODAL_STOP_CONTRACT["model"], 0.0, 256, seed=seed),
                        transport, completion_contract=MODAL_STOP_CONTRACT,
                    )
                    runner = EpisodeRunner(
                        make_environment(seed), condition=arm, episode_seed=seed, provider=provider,
                        seraph_root=seraph_root if arm == "G2" else None,
                        journal_path=output / f"{arm}-seed{seed}-seraph.jsonl" if arm == "G2" else None,
                    )
                    # Capture every turn durably without changing runner scheduling,
                    # dispatch or invalid-episode handling.
                    original_turn = runner._turn

                    def captured_turn(agent, phase, slot):
                        original_turn(agent, phase, slot)
                        save(output / f"{arm}-seed{seed}-progress.json", {
                            "condition": arm, "seed": seed, "provider_inputs": runner.provider_inputs,
                            "provider_exchanges": provider.exchanges, "tool_results": runner.tool_results,
                            "failures": runner.failures, "host_events": runner.stage.research_events(),
                        })

                    runner._turn = captured_turn
                    result = runner.run()
                    result["data_kind"] = "live exploratory grid"
                    result["wire_requests"] = len(events) - start
                    result["provider_attempts"] = provider.transport_attempts
                    result["manifest"]["inference_calls"] = result["wire_requests"]
                    result["manifest"]["completion_contract"] = MODAL_STOP_CONTRACT
                    result["coalition"] = runner.stage.coalition
                    save(output / f"{arm}-seed{seed}.json", result)
                    episodes.append(result)
                    print(json.dumps({"condition": arm, "seed": seed,
                        "valid": result["valid_for_comparison"], "failures": len(result["failures"]),
                        "joint_reward": result["final_summary"].get("joint_reward"),
                        "wire_requests": len(events)}), flush=True)
                finally:
                    os.chdir(cwd)
            if fatal:
                break
    except Exception as exc:
        fatal = type(exc).__name__
    finally:
        os.chdir(cwd)
        try:
            shutdown = worker.close.remote()
        except Exception as exc:
            shutdown = {"error_type": type(exc).__name__, "verify_app_shutdown": True}
        attempted = [(r["condition"], r["episode_seed"]) for r in episodes]
        save(output / "summary.json", {
            "scope": freeze["scope"], "planned_episodes": 15,
            "recorded_episodes": len(episodes), "valid_episodes": sum(r["valid_for_comparison"] for r in episodes),
            "not_recorded_cells": [cell for cell in cells if cell not in attempted],
            "wire_requests": len(events), "fatal_transport_error": fatal, "shutdown": shutdown,
            "P": freeze["P"], "gate0_passed": False,
            "output_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in output.iterdir() if p.is_file()},
        })
        print(json.dumps({"recorded_episodes": len(episodes), "wire_requests": len(events),
                          "fatal": fatal, "shutdown": shutdown}), flush=True)
