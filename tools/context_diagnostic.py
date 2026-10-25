"""Frozen8-call full-context receiver diagnosis: no task mutations, no network here."""

import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "docs/protocol/EXPERIMENT_2_CONTEXT_DIAGNOSTIC_v1.json"
sys.path.insert(0, str(ROOT / "colosseum"))
from experiments.collusion.apart_2026.provider import (  # noqa: E402
    MODAL_STOP_CONTRACT,
    parse_response,
)


class InvalidDiagnostic(ValueError):
    pass


def spec():
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def wire(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def parse(raw, cell):
    calls, error = parse_response(
        raw, model=MODAL_STOP_CONTRACT["model"], completion_contract=MODAL_STOP_CONTRACT
    )
    if error or len(calls) != 1:
        raise InvalidDiagnostic(error or "exactly one tool call required")
    fn = cell["request"]["tools"][0]["function"]
    args = calls[0]["arguments"]
    if calls[0]["name"] != fn["name"] or set(args) != set(fn["parameters"]["required"]):
        raise InvalidDiagnostic("offered tool and exact argument keys required")
    for k, v in args.items():
        if type(v) is not str or v not in fn["parameters"]["properties"][k]["enum"]:
            raise InvalidDiagnostic("string enum argument required")
    return copy.deepcopy(args) if cell["mode"] == "extract_bits" else args["answer"]


def source_files():
    return [
        SPEC_PATH,
        Path(__file__),
        ROOT / "tools/modal_context_diagnostic.py",
        ROOT / "tools/test_context_diagnostic.py",
        ROOT / "tools/modal_shakedown.py",
        ROOT / "colosseum/experiments/collusion/apart_2026/provider.py",
    ]


def record_outcome(raw, cell):
    answer = parse(raw, cell)
    return {
        "answer": answer,
        "correct": answer == cell["expected"],
        "expected": cell["expected"],
    }


def summary(rows):
    return {
        mode: {
            "attempted": sum(r["mode"] == mode for r in rows),
            "valid": sum(r["mode"] == mode and r.get("valid", False) for r in rows),
            "correct": sum(r["mode"] == mode and r.get("correct", False) for r in rows),
            "invalid": sum(r["mode"] == mode and not r.get("valid", False) for r in rows),
            "answers": [r.get("answer") for r in rows if r["mode"] == mode],
        }
        for mode in ("extract_bits", "xor_report")
    }


def payload_for_review(cell):
    """Return a copy so no caller can silently modify frozen requests in place."""
    return copy.deepcopy(cell["request"])


def run_cells(cells, transport, persist):
    """One request/cell, durable raw evidence, and first-invalid global stop."""
    if len(cells) != 8:
        raise ValueError("exactly8frozen cells required")
    import hashlib

    state = {"rows": [], "requests": 0, "complete": False, "stop_reason": None}
    events = []
    for index, cell in enumerate(cells):
        request_text = wire(payload_for_review(cell))
        event = {
            "index": index,
            "mode": cell["mode"],
            "a": cell["a"],
            "b": cell["b"],
            "request_text": request_text,
            "request_sha256": hashlib.sha256(request_text.encode()).hexdigest(),
        }
        row = {
            "index": index,
            "mode": cell["mode"],
            "a": cell["a"],
            "b": cell["b"],
            "expected": cell["expected"],
            "valid": False,
        }
        state["rows"].append(row)
        events.append(event)
        state["requests"] += 1
        persist(state, events)
        try:
            result = transport(request_text)
            event.update(result)
            event["response_sha256"] = hashlib.sha256(result["raw"].encode()).hexdigest()
            persist(state, events)
            if result["http_status"] != 200 or any(
                result[k] != MODAL_STOP_CONTRACT[k] for k in ("model", "revision", "image", "vllm")
            ):
                raise RuntimeError("HTTP or route mismatch")
            row.update(record_outcome(result["raw"], cell), valid=True)
        except Exception as exc:
            row["failure"] = {"type": type(exc).__name__, "message": str(exc)}
            state["stop_reason"] = (
                "first invalid response"
                if isinstance(exc, InvalidDiagnostic)
                else "fatal transport/integrity error"
            )
            persist(state, events)
            break
        persist(state, events)
    state["complete"] = len(state["rows"]) == 8 and all(r["valid"] for r in state["rows"])
    state["summary"] = summary(state["rows"])
    persist(state, events)
    return state, events
