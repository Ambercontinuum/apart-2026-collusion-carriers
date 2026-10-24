"""Native assignment equivalence and permit-boundary attacks."""

import copy
from dataclasses import replace
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from .functional_bridge import CertifiedAssignment, native_assignment
from .preview import PreviewStage, functional_digest
from .runner import make_environment
from .seraph_bridge import CertifiedEmitter

SERAPH_ROOT = Path(os.environ.get(
    "APART_SERAPH_ROOT", Path(__file__).resolve().parents[4] / ".runtime/SERAPH-1.0"
))


class FunctionalBindingTest(unittest.TestCase):
    def setUp(self):
        self.cwd = Path.cwd()
        self.tmp = tempfile.TemporaryDirectory()
        os.chdir(self.tmp.name)
        self.addCleanup(self.restore)

    def restore(self):
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def binding(self, seed=1):
        stage = PreviewStage(make_environment(seed), condition="G2", episode_seed=seed)
        return CertifiedAssignment(CertifiedEmitter(stage, source_root=SERAPH_ROOT))

    def test_native_result_and_state_equivalence(self):
        for seed in (1, 2, 3):
            binding = self.binding(seed)
            control = copy.deepcopy(binding.env)
            for index, agent in enumerate(binding.env.agent_names):
                args = {"task_id": "skip" if index == 3 else sorted(control.tasks)[index]}
                before = functional_digest(binding.env)
                permit = binding.authorize(agent, args)
                self.assertEqual(functional_digest(binding.env), before)
                actual = binding.execute(permit)
                self.assertEqual(actual, native_assignment(control, agent, args))
                self.assertEqual(functional_digest(binding.env), functional_digest(control))
            self.assertEqual(binding.env.get_final_summary(), control.get_final_summary())

    def test_stale_native_state_prevents_execution(self):
        binding = self.binding()
        permit = binding.authorize(binding.env.agent_names[0], {"task_id": "skip"})
        binding.env.priority_bonus += 1
        before = functional_digest(binding.env)
        with self.assertRaises(Exception):
            binding.execute(permit)
        self.assertEqual(functional_digest(binding.env), before)

    def test_arguments_copied_and_replay_rejected(self):
        binding = self.binding()
        agent = binding.env.agent_names[0]
        args = {"task_id": "skip"}
        permit = binding.authorize(agent, args)
        args["task_id"] = sorted(binding.env.tasks)[0]
        self.assertEqual(binding.execute(permit)["result"]["task_id"], None)
        before = functional_digest(binding.env)
        with self.assertRaises(Exception):
            binding.execute(permit)
        self.assertEqual(functional_digest(binding.env), before)

    def test_mutated_permit_rejected(self):
        binding = self.binding()
        permit = binding.authorize(binding.env.agent_names[0], {"task_id": "skip"})
        before = functional_digest(binding.env)
        with self.assertRaises(Exception):
            binding.execute(replace(permit, call_digest="mutated"))
        self.assertEqual(functional_digest(binding.env), before)

    def test_divergent_native_effect_halts_and_does_not_return_result(self):
        binding = self.binding()
        permit = binding.authorize(binding.env.agent_names[0], {"task_id": "skip"})
        with patch.object(binding.env, "apply_state_updates", return_value=None):
            with self.assertRaises(Exception):
                binding.execute(permit)
        self.assertTrue(binding.halted)
        with self.assertRaises(PermissionError):
            binding.authorize(binding.env.agent_names[1], {"task_id": "skip"})

    def test_native_failure_is_returned_without_retry(self):
        binding = self.binding()
        agent = binding.env.agent_names[0]
        before = functional_digest(binding.env)
        result = binding.assign(agent, {"task_id": "unknown-task"})
        self.assertEqual(result["status"], "retry")
        self.assertEqual(functional_digest(binding.env), before)


if __name__ == "__main__":
    unittest.main()
