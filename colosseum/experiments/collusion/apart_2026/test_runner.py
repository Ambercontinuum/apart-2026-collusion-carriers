"""End-to-end scripted turn loop and real pinned SERAPH integration proofs."""

import copy
from dataclasses import replace
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from .runner import EpisodeRunner, ScriptedProvider, make_environment
from .preview import PreviewStage
from .seraph_bridge import CertifiedEmitter

SERAPH_ROOT = Path(
    os.environ.get("APART_SERAPH_ROOT", Path(__file__).resolve().parents[5] / "vendor/SERAPH-1.0")
)


class RunnerTest(unittest.TestCase):
    def setUp(self):
        self.cwd = Path.cwd()
        self.tmp = tempfile.TemporaryDirectory()
        os.chdir(self.tmp.name)
        self.addCleanup(self.restore)

    def restore(self):
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def runner(self, condition="B2", seed=1, provider_cls=ScriptedProvider):
        env = make_environment(seed)
        return EpisodeRunner(
            env,
            condition=condition,
            episode_seed=seed,
            provider=provider_cls(env),
            seraph_root=SERAPH_ROOT if condition == "G2" else None,
        )

    def fill(self, stage):
        for agent in stage.agents:
            for _ in range(4):
                result = stage.handle_tool_call(
                    "preview_task", agent, {"task_id": stage.task_id, "carrier_symbol": 3}, phase="preview"
                )
                self.assertEqual(result["status"], "success")

    def test_all_b_arms_have_twenty_turns_and_identical_native_results(self):
        for seed in (1, 2, 3):
            baseline = None
            for condition in ("B0", "B1", "B2", "B2-S", "G2"):
                result = self.runner(condition, seed).run()
                self.assertTrue(result["valid_for_comparison"], result["failures"])
                self.assertEqual(result["manifest"]["inference_calls"], 0)
                self.assertEqual(len(result["provider_inputs"]), 20)
                self.assertEqual(len(result["tool_results"]), 20)
                summary = result["final_summary"]
                if baseline is None:
                    baseline = summary
                self.assertEqual(summary, baseline)

    def test_no_native_board_posts_and_only_offered_schema_is_used(self):
        runner = self.runner("B2-S")
        with patch(
            "terrarium.blackboard.Megaboard.log_action_to_blackboards",
            side_effect=AssertionError("raw native board echo"),
        ):
            result = runner.run()
        self.assertTrue(result["valid_for_comparison"])
        self.assertEqual(runner.env.communication_protocol.tool_events, [])
        for request in result["provider_inputs"]:
            self.assertEqual(len(request["tools"]), 1)
            expected = "preview_task" if request["phase"] == "preview" else "assign_task"
            self.assertEqual(request["tools"][0]["function"]["name"], expected)
            for message in request["messages"]:
                if message["role"] == "user":
                    view = json.loads(message["content"].split("PEER_INFORMATION_JSON:\n")[1])
                    if request["phase"] == "preview":
                        self.assertEqual(view, [])
                    for row in view:
                        self.assertEqual(set(row), {"sender", "task_id", "slot", "symbol"})

    def test_g2_peer_input_noninterference_under_changed_sender_choices(self):
        class AlterFirstSender(ScriptedProvider):
            def complete(self, **request):
                response = super().complete(**request)
                if request["phase"] == "preview" and request["agent"] == self.agents[0]:
                    response["tool_calls"][0]["arguments"]["carrier_symbol"] = 3
                return response

        first = self.runner("G2")
        second = self.runner("G2", provider_cls=AlterFirstSender)
        a, b = first.run(), second.run()
        recipient = first.stage.agents[1]
        inputs_a = [r for r in a["provider_inputs"] if r["agent"] == recipient]
        inputs_b = [r for r in b["provider_inputs"] if r["agent"] == recipient]
        self.assertEqual(inputs_a, inputs_b)
        self.assertTrue(first.emitter.runtime.journal.verify())
        self.assertTrue(second.emitter.runtime.journal.verify())
        final = inputs_a[-1]["messages"][-1]["content"]
        view = json.loads(final.split("PEER_INFORMATION_JSON:\n")[1])
        self.assertTrue(view)
        self.assertTrue(all(row["symbol"] == 0 for row in view))

    def test_scrambled_provider_view_matches_received_not_raw_order(self):
        runner = self.runner("B2-S")
        result = runner.run()
        prepared = {e["sender"]: e for e in result["host_events"] if e["phase"] == "delivery_prepared"}
        for request in result["provider_inputs"]:
            if request["phase"] != "execution":
                continue
            view = json.loads(request["messages"][-1]["content"].split("PEER_INFORMATION_JSON:\n")[1])
            for sender in {r["sender"] for r in view}:
                self.assertEqual(
                    [r["symbol"] for r in view if r["sender"] == sender], prepared[sender]["received"]
                )
                self.assertNotIn("original_indices", json.dumps(view))

    def test_two_calls_or_public_text_tool_invalidates_without_retry(self):
        class MultipleCalls(ScriptedProvider):
            def complete(self, **request):
                result = super().complete(**request)
                if request["phase"] == "preview" and request["slot"] == 1:
                    result["tool_calls"] *= 2
                return result

        class PublicText(ScriptedProvider):
            def complete(self, **request):
                result = super().complete(**request)
                if request["phase"] == "preview" and request["slot"] == 1:
                    result["tool_calls"] = [{"name": "post_message", "arguments": {"message": "RAW"}}]
                return result

        for provider_cls in (MultipleCalls, PublicText):
            runner = self.runner(provider_cls=provider_cls)
            result = runner.run()
            self.assertFalse(result["valid_for_comparison"])
            self.assertEqual(len(result["provider_inputs"]), 20)
            self.assertEqual(result["final_summary"]["status"], "complete")
            self.assertTrue(all(runner.stage.peer_view(a) == [] for a in runner.stage.agents))

    def test_missing_governance_evidence_holds_information_but_tasks_execute(self):
        runner = self.runner("G2")
        runner.emitter.evidence_available = False
        result = runner.run()
        self.assertFalse(result["valid_for_comparison"])
        self.assertEqual(result["final_summary"]["status"], "complete")
        self.assertTrue(all(runner.stage.peer_view(a) == [] for a in runner.stage.agents))
        self.assertIn(
            "capability.authorization_denied", [e.event_type for e in runner.emitter.runtime.journal.events]
        )

    def test_native_cost_lookup_failure_is_recorded_and_invalid(self):
        env = make_environment(1)
        env.costs[env.agent_names[0]].pop(sorted(env.tasks)[0])
        stage = PreviewStage(env, condition="B2", episode_seed=1)
        result = stage.handle_tool_call(
            "preview_task", stage.agents[0], {"task_id": stage.task_id, "carrier_symbol": 0}, phase="preview"
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual([e["phase"] for e in stage.research_events()], ["proposed", "failed"])
        self.assertFalse(stage.complete)

    def test_permit_replay_tampering_and_stale_native_state_denied(self):
        for mode in ("replay", "tamper", "args", "stale"):
            env = make_environment(1)
            stage = PreviewStage(env, condition="G2", episode_seed=1)
            emitter = CertifiedEmitter(stage, source_root=SERAPH_ROOT)
            self.fill(stage)
            permit = emitter.authorize(copy.deepcopy(emitter.expected))
            if mode == "replay":
                emitter.runtime.execute(permit)
                self.assertTrue(all(stage.peer_view(a) == [] for a in stage.agents))
                with self.assertRaises(PermissionError):
                    emitter.runtime.execute(permit)
            elif mode == "tamper":
                with self.assertRaises(PermissionError):
                    emitter.runtime.execute(replace(permit, call_digest="mutated"))
                with self.assertRaises(PermissionError):
                    emitter.runtime.execute(permit)
            elif mode == "args":
                batch = emitter.runtime._pending[permit.token].call_args[0]
                batch[stage.agents[0]][0]["symbol"] = 3
                with self.assertRaises(PermissionError):
                    emitter.runtime.execute(permit)
                self.assertTrue(all(not v for v in stage._views.values()))
            else:
                env.assignment[stage.agents[0]] = None
                with self.assertRaises(PermissionError):
                    emitter.runtime.execute(permit)
                self.assertTrue(all(not v for v in stage._views.values()))
            self.assertTrue(emitter.runtime.journal.verify())

    def test_noncanonical_batch_and_omitted_affected_recipient_are_rejected(self):
        env = make_environment(1)
        stage = PreviewStage(env, condition="G2", episode_seed=1)
        emitter = CertifiedEmitter(stage, source_root=SERAPH_ROOT)
        self.fill(stage)
        raw = copy.deepcopy(emitter.expected)
        raw[stage.agents[0]][0]["symbol"] = 3
        with self.assertRaises(PermissionError):
            emitter.authorize(raw)
        proposal = emitter.proposal(emitter.expected)
        incomplete = replace(proposal, affected_inhabitants=(stage.agents[0],))
        certificate = emitter.compiled.evaluate(emitter.read_state(), incomplete)
        self.assertFalse(certificate.proven)
        self.assertTrue(all(stage.peer_view(a) == [] for a in stage.agents))


if __name__ == "__main__":
    unittest.main()
