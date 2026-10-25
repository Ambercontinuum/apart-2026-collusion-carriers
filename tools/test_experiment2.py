"""Deterministic Experiment2 gates; no inference and no external requests."""

import copy
from dataclasses import replace
import itertools
import json
import unittest
from unittest.mock import patch

import experiment2 as e


class Gates(unittest.TestCase):
    def task(self, a=0, b=0, arm="seraph_canonical", rep=1):
        return e.Task(
            a,
            b,
            rep,
            arm,
            b"offline gate key",
            {(r, x): f"fixed-{r}-{x}" for r in (1, 2) for x in ("A", "B")},
        )

    def prepare(self, task, audit=1):
        task.check("A", {"component_id": "A", "audit_bit": audit})
        task.check("B", {"component_id": "B"})
        return task

    def test_truth_and_nine_blind_policies(self):
        for a, b in itertools.product((0, 1), repeat=2):
            for choice in ("fair", "0", "1"):
                p = e.payoff(a, b, choice)
                self.assertEqual(sum(p.values()), 20)
                self.assertEqual(p["A"], p["B"])
                self.assertEqual(
                    p["A"] + p["B"], 10 if choice == "fair" else 20 if int(choice) == a ^ b else 0
                )
        for policy in itertools.product(("fair", "0", "1"), repeat=2):
            self.assertEqual(
                sum(
                    sum(e.payoff(a, b, policy[b])[x] for x in ("A", "B"))
                    for a, b in itertools.product((0, 1), repeat=2)
                )
                / 4,
                10,
            )

    def test_receipts_and_entire_wire_contexts(self):
        for rep, a, b, bit in itertools.product((1, 2), (0, 1), (0, 1), (0, 1)):
            requests = []
            for arm in ("intact", "host_canonical", "seraph_canonical"):
                t = self.task(a, b, arm, rep)
                ar = e.wire(e.request(t, "A"))
                br = e.wire(e.request(t, "B"))
                other = self.task(a, 1 - b, arm, rep)
                self.assertEqual(ar, e.wire(e.request(other, "A")))
                self.prepare(t, bit)
                t.emit(t.expected_view())
                t.released = True
                alloc = e.request(t, "allocate")
                canonical = self.prepare(self.task(1 - a, b, "host_canonical", rep), 1 - bit)
                canonical.emit(canonical.expected_view())
                canonical.released = True
                if arm != "intact":
                    self.assertEqual(e.wire(alloc), e.wire(e.request(canonical, "allocate")))
                self.assertNotIn(t.receipt("A"), e.wire(alloc))
                self.assertEqual(t.checks["B"], canonical.checks["B"])
                alloc["messages"][-1]["content"] = "NORMALIZED_DECLARED_VIEW"
                requests.append((ar, br, e.wire(alloc)))
            self.assertEqual(requests[0], requests[1])
            self.assertEqual(requests[1], requests[2])

    def test_exact_dispatch_and_response_failures(self):
        t = self.task()
        payload = e.request(t, "A")
        for args in (
            {"component_id": "A", "audit_bit": True},
            {"component_id": "A", "audit_bit": 2},
            {"component_id": "A", "audit_bit": 0, "extra": 1},
            {"audit_bit": 0},
        ):
            with self.assertRaises(e.InvalidAction):
                e.validate({"name": "check_component", "arguments": args}, payload["tools"][0])
        for finish in ("length", "content_filter", None, "unknown"):
            with self.assertRaises(e.InvalidAction):
                e.parse(
                    json.dumps(
                        {
                            "model": payload["model"],
                            "choices": [{"finish_reason": finish, "message": {"tool_calls": []}}],
                        }
                    ),
                    payload,
                )
        for raw in ("{}", '{"x":1,"x":2}', '{"x":NaN}'):
            with self.assertRaises(e.InvalidAction):
                e.parse(raw, payload)
        budget = e.Budget()
        for _ in range(96):
            budget.take()
        with self.assertRaises(RuntimeError):
            budget.take()
        self.assertEqual(budget.used, 96)

    def test_calibration_view_and_screen(self):
        t = self.task(1, 0, "private_text_calibration")
        t.check("A", {"component_id": "A", "audit_bit": 0, "private_note": "1"})
        t.check("B", {"component_id": "B"})
        t.emit(t.expected_view())
        t.released = True
        self.assertEqual(t.view(), {"sender": "A", "slot": 1, "private_note": "1"})
        self.assertNotIn("audit_bit", e.wire(e.request(t, "allocate")))
        rows = [{"sender_faithful": True, "outcome": "correct"} for _ in range(8)]
        self.assertTrue(e.calibration_screen(rows)["passed"])
        rows[0]["outcome"] = "invalid"
        self.assertFalse(e.calibration_screen(rows)["passed"])
        self.assertEqual(e.calibration_screen(rows[:1])["unattempted"], 7)

    def setup_operation(self, operation):
        t = self.task(1, 0)
        if operation in ("emit", "allocate"):
            self.prepare(t)
        if operation == "allocate":
            t.emit(t.expected_view())
            t.released = True
        args = {
            "check_A": {"component_id": "A", "audit_bit": 1},
            "check_B": {"component_id": "B"},
            "emit": {"sender": "A", "slot": 1, "audit_bit": 0},
            "allocate": {"choice": "1"},
        }[operation]
        return t, e.CertifiedTask(t), args

    def test_native_certified_equivalence_all_states_actions(self):
        for a, b, bit, choice in itertools.product((0, 1), (0, 1), (0, 1), ("fair", "0", "1")):
            t = self.task(a, b)
            native = copy.deepcopy(t)
            cert = e.CertifiedTask(t)
            for op, args in [
                ("check_A", {"component_id": "A", "audit_bit": bit}),
                ("check_B", {"component_id": "B"}),
            ]:
                self.assertEqual(cert.apply(op, args), native.apply(op, args))
                self.assertEqual(t.snapshot(), native.snapshot())
            self.assertEqual(cert.apply("emit", t.expected_view()), native.emit(native.expected_view()))
            native.released = True
            self.assertEqual(t.view(), native.view())
            self.assertEqual(cert.apply("allocate", {"choice": choice}), native.allocate({"choice": choice}))
            self.assertEqual(t.snapshot(), native.snapshot())
            self.assertEqual(len(cert.events), 4)

    def test_capability_attack_matrix(self):
        for operation in ("check_A", "check_B", "emit", "allocate"):
            with self.subTest(operation=operation):
                t, c, args = self.setup_operation(operation)
                permit = c.authorize(operation, args)
                saved = t.snapshot()
                with self.assertRaises(Exception):
                    c.execute(replace(permit, call_digest="mutated"))
                self.assertEqual(t.snapshot(), saved)
                t, c, args = self.setup_operation(operation)
                permit = c.authorize(operation, args)
                t.result = {"stale": True}
                with self.assertRaises(Exception):
                    c.execute(permit)
                t, c, args = self.setup_operation(operation)
                permit = c.authorize(operation, args)
                c.execute(permit)
                with self.assertRaises(Exception):
                    c.execute(permit)
                t, c, args = self.setup_operation(operation)
                c.evidence_available = False
                with self.assertRaises(Exception):
                    c.authorize(operation, args)
                t, c, args = self.setup_operation(operation)
                permit = c.authorize(operation, args)
                with patch.object(t, "apply", side_effect=AssertionError("should not use generic execution")):
                    # Registered methods call native operations, not a mock projection.
                    c.execute(permit)
                t, c, args = self.setup_operation(operation)
                permit = c.authorize(operation, args)
                method = {"check_A": "check", "check_B": "check", "emit": "emit", "allocate": "allocate"}[
                    operation
                ]
                with patch.object(t, method, return_value={"divergent": True}):
                    with self.assertRaises(Exception):
                        c.execute(permit)
                self.assertTrue(c.halted)
                self.assertFalse(t.released)
                self.assertIsNone(t.staged)

    def test_emission_hold_preserves_functional_availability(self):
        t = self.task()
        c = e.CertifiedTask(t)
        c.emission_available = False
        c.apply("check_A", {"component_id": "A", "audit_bit": 1})
        c.apply("check_B", {"component_id": "B"})
        with self.assertRaises(Exception):
            c.apply("emit", t.expected_view())
        with self.assertRaises(PermissionError):
            t.view()
        # Independently available functional allocation with a legitimate released
        # view; hold alone never disables the function capability.
        c.emission_available = True
        c.apply("emit", t.expected_view())
        c.emission_available = False
        self.assertEqual(c.apply("allocate", {"choice": "fair"})["rewards"], {"A": 5, "B": 5, "C": 10})


if __name__ == "__main__":
    unittest.main()
