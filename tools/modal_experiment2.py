"""Fail-closed Experiment2 execution preflight. No Modal worker is launched.

The pinned backend ignores parallel_tool_calls. A new reviewed execution
contract and live driver are required; this module never bypasses that gate.
"""

import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    record = json.loads((root / "evidence/experiment2/v1_1/GATES.json").read_text())
    if not record.get("live_execution_ready"):
        raise SystemExit("Experiment2 stopped before inference: " + record["stop_reason"])
    raise SystemExit("Live driver not released: backend contract amendment required first.")


if __name__ == "__main__":
    main()
