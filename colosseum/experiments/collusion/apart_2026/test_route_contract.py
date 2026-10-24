import copy
import json
import unittest

from .provider import MODAL_STOP_CONTRACT, LiveProvider, ProviderConfig, parse_response


class RouteContractTest(unittest.TestCase):
    def raw(self, status="stop", arguments='{"value":1}', count=1):
        return json.dumps({"model": MODAL_STOP_CONTRACT["model"], "choices": [{
            "finish_reason": status, "message": {"tool_calls": [
                {"type": "function", "function": {"name": "ping", "arguments": arguments}}
            ] * count}}]})

    def test_stop_requires_exact_contract_and_preserves_raw(self):
        raw = self.raw()
        self.assertEqual(parse_response(raw, model=MODAL_STOP_CONTRACT["model"])[0], [])
        provider = LiveProvider(ProviderConfig(MODAL_STOP_CONTRACT["model"], 0, 256),
                                lambda _: raw, completion_contract=MODAL_STOP_CONTRACT)
        result = provider.complete(messages=[], tools=[], agent="a", phase="preview", slot=1)
        self.assertEqual(len(result["tool_calls"]), 1)
        self.assertEqual(provider.exchanges[0]["raw_response"], raw)
        self.assertEqual(json.loads(raw)["choices"][0]["finish_reason"], "stop")

    def test_adverse_statuses_and_payloads_rejected(self):
        cases = [self.raw(status=s) for s in ("length", "content_filter", None, "unknown")]
        cases += [self.raw(count=0), self.raw(count=2), self.raw(arguments="invalid"),
                  self.raw(arguments='{"x":1,"x":2}')]
        for raw in cases:
            calls, reason = parse_response(raw, model=MODAL_STOP_CONTRACT["model"],
                                           completion_contract=MODAL_STOP_CONTRACT)
            self.assertEqual(calls, [])
            self.assertIsNotNone(reason)

    def test_mutated_route_contract_rejected(self):
        contract = copy.deepcopy(MODAL_STOP_CONTRACT)
        contract["revision"] = "different"
        with self.assertRaises(ValueError):
            LiveProvider(ProviderConfig(MODAL_STOP_CONTRACT["model"], 0, 256),
                         lambda _: self.raw(), completion_contract=contract)
