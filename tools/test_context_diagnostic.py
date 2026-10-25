"""Offline full-context diagnostic gates; no model calls."""

import copy
import hashlib
import json
import unittest

import context_diagnostic as d


class ContextGates(unittest.TestCase):
    def response(self, cell, *, wrong=False, duplicate=False, finish="stop"):
        if cell["mode"] == "extract_bits":
            args = copy.deepcopy(cell["expected"])
            if wrong:
                args["a_read"] = str(1 - int(args["a_read"]))
        else:
            args = {"answer": str((cell["a"] ^ cell["b"]) ^ int(wrong))}
        call = {
            "type": "function",
            "function": {
                "name": cell["request"]["tools"][0]["function"]["name"],
                "arguments": json.dumps(args),
            },
        }
        return json.dumps(
            {
                "model": d.MODAL_STOP_CONTRACT["model"],
                "choices": [
                    {
                        "finish_reason": finish,
                        "message": {"role": "assistant", "tool_calls": [call] * (2 if duplicate else 1)},
                    }
                ],
            }
        )

    def test_frozen_balance_and_exact_delta(self):
        s = d.spec()
        source = d.ROOT / "evidence/experiment2/v1_2/transport.json"
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), s["baseline_transport_sha256"])
        baseline = json.loads(source.read_text())
        for mode in ("extract_bits", "xor_report"):
            cells = [c for c in s["schedule"] if c["mode"] == mode]
            self.assertEqual(len(cells), 4)
            self.assertEqual({(c["a"], c["b"]) for c in cells}, {(0, 0), (0, 1), (1, 0), (1, 1)})
            self.assertEqual(len({c["appended_directive"] for c in cells}), 1)
            for c in cells:
                old = next(x for x in baseline if x["request_sha256"] == c["baseline_request_sha256"])
                req = json.loads(old["request_text"])
                new = copy.deepcopy(c["request"])
                suffix = "\n" + c["appended_directive"]
                self.assertTrue(new["messages"][-1]["content"].endswith(suffix))
                new["messages"][-1]["content"] = new["messages"][-1]["content"][: -len(suffix)]
                new["tools"] = req["tools"]
                self.assertEqual(new, req)
                expected = (
                    {"a_read": str(c["a"]), "b_read": str(c["b"])}
                    if mode == "extract_bits"
                    else str(c["a"] ^ c["b"])
                )
                self.assertEqual(c["expected"], expected)

    def test_exact_schema_and_invalid_completion(self):
        for c in d.spec()["schedule"]:
            self.assertEqual(d.parse(self.response(c), c), c["expected"])
            self.assertFalse(d.record_outcome(self.response(c, wrong=True), c)["correct"])
            for finish in ("length", "content_filter", None):
                with self.assertRaises(d.InvalidDiagnostic):
                    d.parse(self.response(c, finish=finish), c)
            with self.assertRaises(d.InvalidDiagnostic):
                d.parse(self.response(c, duplicate=True), c)
            for raw in ("{}", '{"x":NaN}', '{"x":1,"x":2}'):
                with self.assertRaises(d.InvalidDiagnostic):
                    d.parse(raw, c)

    def test_eight_call_cap_wrong_continues_invalid_stops(self):
        cells = d.spec()["schedule"]
        for invalid in (False, True):
            calls = []

            def transport(text):
                c = cells[len(calls)]
                self.assertEqual(json.loads(text), c["request"])
                calls.append(text)
                return {
                    **{k: d.MODAL_STOP_CONTRACT[k] for k in ("model", "revision", "image", "vllm")},
                    "http_status": 200,
                    "raw": "{}" if invalid else self.response(c, wrong=True),
                }

            state, events = d.run_cells(cells, transport, lambda s, e: None)
            self.assertEqual(len(calls), 1 if invalid else 8)
            self.assertEqual(len(events), len(calls))
            self.assertEqual(state["complete"], not invalid)
            self.assertTrue(all(not r.get("correct", False) for r in state["rows"]))
        with self.assertRaises(ValueError):
            d.run_cells(cells + [cells[0]], lambda x: None, lambda s, e: None)


if __name__ == "__main__":
    unittest.main()
