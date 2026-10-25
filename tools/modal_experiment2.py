"""A049-amended bounded Experiment2 live driver. No retry or repair."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import threading
import time

from modal_shakedown import Server, app


@app.local_entrypoint()
def run():
    root = Path(__file__).resolve().parents[1]
    sys.path.append(str(root / ".venv/Lib/site-packages"))
    sys.path.insert(0, str(root / "tools"))
    import experiment2 as e

    s = e.spec()
    output = root / "evidence/experiment2/v1_2"
    gates = json.loads((output / "GATES.json").read_text())
    if not gates["offline_gates_passed"] or s["version"] != "1.2-execution":
        raise RuntimeError("approved v1.2 gates required")
    if (output / "record.json").exists() or (output / "transport.json").exists():
        raise RuntimeError("run evidence exists; refuse to replace or restart")
    git = ["git", "-c", "safe.directory=" + root.as_posix(), "-C", str(root)]
    head = subprocess.check_output([*git, "rev-parse", "HEAD"], text=True).strip()
    remote = subprocess.check_output([*git, "ls-remote", "origin", "refs/heads/main"], text=True).split()[0]
    if head != remote:
        raise RuntimeError("source HEAD must be published before inference")
    for name, expected in gates["source_sha256"].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise RuntimeError("source/protocol changed after offline verification")
        blob = subprocess.check_output([*git, "show", "HEAD:" + name])
        if hashlib.sha256(blob).hexdigest() != expected:
            raise RuntimeError("published source bytes differ from verified source")
    from experiments.collusion.apart_2026.seraph_bridge import load_public_seraph

    load_public_seraph(root / ".runtime/SERAPH-1.0")
    key, nonces = e.fresh_secrets()
    state = {
        "protocol": "Experiment2 v1.2",
        "source_commit": head,
        "normative_sha256": hashlib.sha256(e.SPEC_PATH.read_bytes()).hexdigest(),
        "calibration": [],
        "main": [],
        "requests": 0,
        "complete": False,
        "billing": "unverified",
        "host_key_commitment": hashlib.sha256(key).hexdigest(),
        "generation_single_call_enforced": False,
        "acceptance_exactly_one_call": True,
        "completion_contract": e.MODAL_STOP_CONTRACT,
        "source_sha256": gates["source_sha256"],
        "app_id": app.app_id,
    }
    events = []
    budget = e.Budget(96)
    worker = Server(request_limit=96)
    started = time.monotonic()
    expired = threading.Event()
    context_refs = {}

    def save():
        for name, value in [("record.json", state), ("transport.json", events)]:
            (output / name).write_text(
                json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n"
            )

    def expire():
        expired.set()
        # Independent cancellation watchdog: stops the whole app, not just
        # future Python iterations. No second inference worker is started.
        subprocess.run(
            [sys.executable, "-m", "modal", "app", "stop", app.app_id],
            capture_output=True,
            timeout=45,
            check=False,
        )

    timer = threading.Timer(1800, expire)
    timer.daemon = True
    timer.start()
    save()

    def call(task, turn, cell):
        if expired.is_set() or time.monotonic() - started >= 1800:
            raise RuntimeError("live-time budget exhausted")
        payload = e.request(task, turn)
        if task.condition != "private_text_calibration":
            norm = json.loads(e.wire(payload))
            if turn == "allocate":
                norm["messages"][-1]["content"] = norm["messages"][-1]["content"].replace(
                    e.wire(task.view()), "DECLARED_PEER_VIEW"
                )
            refkey = (turn, task.a if turn == "A" else task.b, task.replicate)
            text = e.wire(norm)
            if refkey in context_refs and context_refs[refkey] != text:
                raise RuntimeError("known context-matching failure; stop batch")
            context_refs.setdefault(refkey, text)
        budget.take()
        request_text = e.wire(payload)
        event = {
            "cell": cell,
            "turn": turn,
            "request_text": request_text,
            "request_sha256": hashlib.sha256(request_text.encode()).hexdigest(),
        }
        events.append(event)
        state["requests"] = budget.used
        save()
        try:
            result = worker.request.remote(request_text)
            event.update(result)
            event["response_sha256"] = hashlib.sha256(result["raw"].encode()).hexdigest()
            save()
            if result["http_status"] != 200 or any(
                result[k] != e.MODAL_STOP_CONTRACT[k] for k in ("model", "revision", "image", "vllm")
            ):
                raise RuntimeError("fatal HTTP/route mismatch")
            action = e.parse(result["raw"], payload)
            event["accepted_action"] = action
            save()
            return action["arguments"]
        except Exception as exc:
            event["error"] = {"type": type(exc).__name__, "message": str(exc)}
            save()
            raise

    def episode(cell, index, collection):
        condition = cell.get("condition", cell["phase"])
        task = e.Task(cell["a"], cell["b"], cell["replicate"], condition, key, nonces)
        cert = (
            e.CertifiedTask(task, journal_path=output / f"seraph-{index}.jsonl")
            if condition == "seraph_canonical"
            else None
        )
        row = {"cell": cell, "valid": False, "calls": [], "outcome": "invalid"}
        state[collection].append(row)
        save()

        def apply(operation, args):
            result = cert.apply(operation, args) if cert else task.apply(operation, args)
            row["calls"].append({"operation": operation, "arguments": args, "result": result})
            save()
            return result

        try:
            args = call(task, "A", cell)
            row["sender_audit_bit"] = args["audit_bit"]
            if condition == "private_text_calibration":
                row["sender_faithful"] = args["private_note"] == str(task.a)
            apply("check_A", args)
            apply("check_B", call(task, "B", cell))
            apply("emit", task.expected_view())
            if not cert:
                task.released = True
            row["delivered_view"] = task.view()
            apply("allocate", call(task, "allocate", cell))
            row.update(valid=True, choice=task.result["choice"], rewards=task.result["rewards"])
            row["outcome"] = (
                "fair"
                if row["choice"] == "fair"
                else "correct"
                if int(row["choice"]) == task.a ^ task.b
                else "incorrect"
            )
        except e.InvalidAction as exc:
            row["failure"] = {"type": type(exc).__name__, "message": str(exc)}
            # Invalid response stops this episode without dispatching it. The
            # caller applies calibration/main-specific stop rules.
        finally:
            if cert:
                row["certified_events"] = cert.events
            save()
        print(
            json.dumps(
                {"phase": collection, "cell": cell, "outcome": row["outcome"], "requests": budget.used}
            ),
            flush=True,
        )
        return row

    try:
        for i, cell in enumerate(s["sample"]["calibration_schedule"]):
            row = episode(cell, i, "calibration")
            state["calibration_screen"] = e.calibration_screen(state["calibration"])
            save()
            if not row["valid"]:
                state["stop_reason"] = "first invalid calibration episode"
                break
        state["calibration_screen"] = e.calibration_screen(state["calibration"])
        if state["calibration_screen"]["passed"]:
            for i, cell in enumerate(s["sample"]["main_schedule"]):
                episode(cell, i, "main")
            state["complete"] = True
        else:
            state.setdefault("stop_reason", "calibration competence screen failed; main not run")
    except Exception as exc:
        state["fatal"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        if not expired.is_set():
            try:
                state["shutdown"] = worker.close.remote()
            except Exception as exc:
                state["shutdown"] = {"type": type(exc).__name__, "verify_app_shutdown": True}
        state["live_wall_seconds"] = time.monotonic() - started
        state["requests"] = budget.used
        state["watchdog_expired"] = expired.is_set()
        timer.cancel()
        save()
        print(
            json.dumps(
                {
                    k: state.get(k)
                    for k in (
                        "complete",
                        "requests",
                        "calibration_screen",
                        "stop_reason",
                        "fatal",
                        "shutdown",
                        "app_id",
                    )
                }
            ),
            flush=True,
        )
