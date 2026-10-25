"""Reuse the established task and full-driver tests on the final prompt/driver.

All responses are scripted. Owner approval is simulated only in this test process;
the actual pending protocol file is unchanged. No Modal import/worker/inference.
"""

import copy
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import experiment2 as e


def main():
    e.SPEC_PATH = e.ROOT / "docs/protocol/EXPERIMENT_2_FINAL_ATTEMPT_v1.json"
    pending = e.spec()
    assert not pending.get("execution_authorized") or pending.get("authorization")
    fake_approved = copy.deepcopy(pending)
    fake_approved["execution_authorized"] = True
    source = (e.ROOT / "tools/test_experiment2.py").read_text(encoding="utf-8")
    source = source.replace("tools/modal_experiment2.py", "tools/modal_final_attempt.py").replace(
        "evidence/experiment2/v1_2", "evidence/experiment2/final-attempt-v1"
    )
    source = source.replace("private bit b is ([01])", "(?:private )?bit b(?: is |=)([01])")
    module = types.ModuleType("final_attempt_adapted_tests")
    exec(compile(source, str(e.ROOT / "tools/test_experiment2.py"), "exec"), module.__dict__)
    with patch.object(e, "spec", side_effect=lambda: copy.deepcopy(fake_approved)):
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromModule(module)
        )
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
