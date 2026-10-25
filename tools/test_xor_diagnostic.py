"""Checks frozen diagnostic requests, strict acceptance and12/first-invalid caps."""

import copy
import hashlib
import json
import unittest

import xor_diagnostic as d


class DiagnosticGates(unittest.TestCase):
    def response(self, cell, value=None, finish="stop", duplicate=False):
        value = cell["expected"] if value is None else value
        if cell["mode"] == "xor_text":
            message = {"role": "assistant", "content": value}
        else:
            fn = cell["request"]["tools"][0]["function"]
            key = fn["parameters"]["required"][0]
            calls = [
                {"type": "function", "function": {"name": fn["name"], "arguments": json.dumps({key: value})}}
            ]
            message = {"role": "assistant", "tool_calls": calls * (2 if duplicate else 1)}
        return json.dumps(
            {
                "model": d.MODAL_STOP_CONTRACT["model"],
                "choices": [{"finish_reason": finish, "message": message}],
            }
        )

    def test_complete_balanced_frozen_cases_and_oracle_delta(self):
        s = d.spec()
        source = d.ROOT / "evidence/experiment2/v1_2/transport.json"
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), s["baseline_transport_sha256"])
        old = json.loads(source.read_text())
        for mode in ("xor_text", "xor_tool", "allocation_oracle"):
            cells = [c for c in s["schedule"] if c["mode"] == mode]
            self.assertEqual({(c["a"], c["b"]) for c in cells}, {(0, 0), (0, 1), (1, 0), (1, 1)})
            self.assertEqual(len(cells), 4)
            for c in cells:
                self.assertEqual(c["expected"], str(c["a"] ^ c["b"]))
                self.assertEqual(c["request"]["seed"], 1)
                self.assertEqual(c["request"]["max_tokens"], 256)
                self.assertFalse(c["request"]["parallel_tool_calls"])
                if mode == "allocation_oracle":
                    ev = next(x for x in old if x["request_sha256"] == c["baseline_request_sha256"])
                    baseline = json.loads(ev["request_text"])
                    candidate = copy.deepcopy(c["request"])
                    prefix, oracle = candidate["messages"][-1]["content"].split("\nDIAGNOSTIC ORACLE: ")
                    self.assertIn(f'choice="{c["expected"]}"', oracle)
                    candidate["messages"][-1]["content"] = prefix
                    self.assertEqual(candidate, baseline)

    def test_strict_text_and_tool_acceptance(self):
        for c in d.spec()["schedule"]:
            self.assertEqual(d.parse(self.response(c), c), c["expected"])
            for finish in ("length", "content_filter", None):
                with self.assertRaises(d.InvalidDiagnostic):
                    d.parse(self.response(c, finish=finish), c)
            for raw in ("{}", '{"x":NaN}', '{"x":1,"x":2}'):
                with self.assertRaises(d.InvalidDiagnostic):
                    d.parse(raw, c)
            if c["mode"] == "xor_text":
                for value in ("answer: 0", "fair", ""):
                    with self.assertRaises(d.InvalidDiagnostic):
                        d.parse(self.response(c, value=value), c)
            else:
                with self.assertRaises(d.InvalidDiagnostic):
                    d.parse(self.response(c, duplicate=True), c)

    def test_one_request_per_cell_and_first_invalid_stop(self):
        cells = d.spec()["schedule"]
        for invalid in (False, True):
            calls = []
            saves = []

            def transport(text):
                c = cells[len(calls)]
                self.assertEqual(json.loads(text), c["request"])
                calls.append(text)
                return {
                    **{k: d.MODAL_STOP_CONTRACT[k] for k in ("model", "revision", "image", "vllm")},
                    "raw": "{}" if invalid else self.response(c),
                    "http_status": 200,
                }

            state, events = d.run_cells(cells, transport, lambda s, e: saves.append((s["requests"], len(e))))
            self.assertEqual(len(calls), 1 if invalid else 12)
            self.assertEqual(len(events), len(calls))
            self.assertEqual(state["complete"], not invalid)
            self.assertTrue(saves)
            if not invalid:
                self.assertTrue(all(x["correct"] for x in state["rows"]))
        with self.assertRaises(ValueError):
            d.run_cells(cells + [cells[0]], lambda x: None, lambda s, e: None)


if __name__ == "__main__":
    unittest.main()
