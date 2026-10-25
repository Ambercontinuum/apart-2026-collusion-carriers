"""A0538-call full-context receiver diagnostic on pinned Modal route; no native actions."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import threading
import time

from modal_shakedown import Server, app


@app.local_entrypoint()
def diagnose():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "tools"))
    import context_diagnostic as d

    output = root / "evidence/experiment2/context-diagnostic-v1"
    if (output / "record.json").exists() or (output / "transport.json").exists():
        raise RuntimeError("evidence exists; refuse restart/replacement")
    gate = json.loads((output / "GATES.json").read_text())
    if not gate["passed"]:
        raise RuntimeError("offline gates required")
    git = ["git", "-c", "safe.directory=" + root.as_posix(), "-C", str(root)]
    head = subprocess.check_output([*git, "rev-parse", "HEAD"], text=True).strip()
    remote = subprocess.check_output([*git, "ls-remote", "origin", "refs/heads/main"], text=True).split()[0]
    if head != remote:
        raise RuntimeError("publish source before calls")
    for name, expected in gate["source_sha256"].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise RuntimeError("source changed after gates")
        if hashlib.sha256(subprocess.check_output([*git, "show", "HEAD:" + name])).hexdigest() != expected:
            raise RuntimeError("committed source bytes differ")
    s = d.spec()
    baseline = root / "evidence/experiment2/v1_2/transport.json"
    if hashlib.sha256(baseline.read_bytes()).hexdigest() != s["baseline_transport_sha256"]:
        raise RuntimeError("archived calibration source changed")
    meta = {
        "scope": "standalone full-context receiver diagnostic; not main experiment",
        "authorization": "A053",
        "source_commit": head,
        "app_id": app.app_id,
        "protocol_sha256": hashlib.sha256(d.SPEC_PATH.read_bytes()).hexdigest(),
        "source_sha256": gate["source_sha256"],
        "billing": "unverified",
        "worker": "one L4",
        "request_cap": 8,
        "max_output_tokens": 256,
        "generation_single_call_enforced": False,
        "native_actions_executed": 0,
    }
    worker = Server(request_limit=8, required_tools=True)
    started = time.monotonic()
    expired = threading.Event()
    last_state, last_events = {}, []

    def persist(state, events):
        nonlocal last_state, last_events
        last_state, last_events = state, events
        for name, value in [("record.json", {**meta, **state}), ("transport.json", events)]:
            (output / name).write_text(
                json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n"
            )

    def expire():
        expired.set()
        subprocess.run(
            [sys.executable, "-m", "modal", "app", "stop", app.app_id],
            capture_output=True,
            timeout=45,
            check=False,
        )

    def transport(text):
        if expired.is_set() or time.monotonic() - started >= 900:
            raise RuntimeError("900second limit")
        return worker.request.remote(text)

    timer = threading.Timer(900, expire)
    timer.daemon = True
    timer.start()
    try:
        d.run_cells(s["schedule"], transport, persist)
    finally:
        if not expired.is_set():
            try:
                meta["shutdown"] = worker.close.remote()
            except Exception as exc:
                meta["shutdown"] = {"error_type": type(exc).__name__, "verify_app_shutdown": True}
        meta["live_wall_seconds"] = time.monotonic() - started
        meta["watchdog_expired"] = expired.is_set()
        timer.cancel()
        persist(last_state, last_events)
        print(
            json.dumps(
                {
                    key: {**meta, **last_state}.get(key)
                    for key in ("complete", "requests", "summary", "stop_reason", "shutdown", "app_id")
                }
            ),
            flush=True,
        )
