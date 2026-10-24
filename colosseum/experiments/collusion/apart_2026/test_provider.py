"""Live-provider boundary proofs with mocked transport only. No network, credentials or inference."""

import ast
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import unittest

from .provider import LiveProvider, ProviderConfig, parse_response
from .runner import EpisodeRunner, ScriptedProvider, make_environment

CONFIG = ProviderConfig(model="mock/model-a", temperature=0.0, max_tokens=256)


def response_text(calls, model=CONFIG.model, choices=1):
    message = {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {"id": f"t{i}", "type": "function", "function": {"name": name, "arguments": arguments}}
            for i, (name, arguments) in enumerate(calls)
        ],
    }
    return json.dumps({"model": model, "choices": [
        {"index": 0, "message": message, "finish_reason": "tool_calls"}
    ] * choices})


class ScriptedTransport:
    """Answers the exact request text like ScriptedProvider would, in OpenAI wire format."""

    def __init__(self, env, mutate=None):
        self.decider = ScriptedProvider(env)
        self.mutate = mutate
        self.requests = []

    def __call__(self, request_text):
        self.requests.append(request_text)
        request = json.loads(request_text)
        prompt = [m for m in request["messages"] if m["role"] == "user"][-1]["content"]
        agent = re.search(r"You are agent (\S+)", prompt).group(1)
        phase = "preview" if request["tools"][0]["function"]["name"] == "preview_task" else "execution"
        slot = int(re.search(r"Preview slot (\d) of 4", prompt).group(1)) if phase == "preview" else 1
        call = self.decider.complete(messages=request["messages"], tools=request["tools"],
                                     agent=agent, phase=phase, slot=slot)["tool_calls"][0]
        raw = response_text([(call["name"], json.dumps(call["arguments"]))])
        return self.mutate(len(self.requests), raw) if self.mutate else raw


class ParseTest(unittest.TestCase):
    def test_incomplete_filtered_missing_and_unknown_completion_status_rejected(self):
        for status in ("length", "content_filter", "stop", None, "unknown"):
            body = json.loads(response_text([("assign_task", '{"task_id":"skip"}')]))
            body["choices"][0]["finish_reason"] = status
            self.assertInvalid(json.dumps(body), "finish reason")

    def assertInvalid(self, raw, fragment):
        calls, reason = parse_response(raw, model=CONFIG.model)
        self.assertEqual(calls, [])
        self.assertIn(fragment, reason)

    def test_json_string_arguments_parse_once_into_object(self):
        raw = response_text([("preview_task", '{"task_id": "ISSUE-0001::docs", "carrier_symbol": 2}')])
        calls, reason = parse_response(raw, model=CONFIG.model)
        self.assertIsNone(reason)
        self.assertEqual(calls, [{"name": "preview_task",
                                  "arguments": {"task_id": "ISSUE-0001::docs", "carrier_symbol": 2}}])

    def test_double_encoded_arguments_are_not_parsed_twice(self):
        inner = json.dumps({"task_id": "ISSUE-0001::docs", "carrier_symbol": 2})
        self.assertInvalid(response_text([("preview_task", json.dumps(inner))]), "must be a JSON object")

    def test_malformed_or_ambiguous_payloads_are_invalid(self):
        cases = {
            "not json": "tool arguments are not strict JSON",
            '{"carrier_symbol": 1, "carrier_symbol": 3}': "duplicate JSON key",
            '{"carrier_symbol": NaN}': "non-finite",
            '{"carrier_symbol": 1e999}': "non-finite",
            "[1, 2]": "must be a JSON object",
        }
        for arguments, fragment in cases.items():
            self.assertInvalid(response_text([("preview_task", arguments)]), fragment)

    def test_structural_response_failures_are_invalid(self):
        body = json.loads(response_text([("preview_task", "{}")]))
        body["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"] = {"task_id": "x"}
        self.assertInvalid(json.dumps(body), "JSON-string arguments")
        self.assertInvalid(response_text([]), "no tool call")
        self.assertInvalid(response_text([("preview_task", "{}")], choices=2), "exactly one choice")
        self.assertInvalid(response_text([("preview_task", "{}")], model="mock/fallback"), "model differs")
        self.assertInvalid("<html>gateway error</html>", "not strict JSON")
        self.assertInvalid('{"model": "mock/model-a", "choices": [], "model": "x"}', "duplicate JSON key")

    def test_multiple_calls_are_returned_for_the_runner_to_reject(self):
        raw = response_text([("preview_task", "{}"), ("preview_task", "{}")])
        calls, reason = parse_response(raw, model=CONFIG.model)
        self.assertIsNone(reason)
        self.assertEqual(len(calls), 2)


class ProviderTest(unittest.TestCase):
    def test_exact_request_and_raw_response_are_preserved(self):
        raw = response_text([("assign_task", '{"task_id":  "skip"}')])
        seen = []
        provider = LiveProvider(CONFIG, lambda text: seen.append(text) or raw)
        messages = [{"role": "user", "content": "hi"}]
        tools = [{"type": "function", "function": {"name": "assign_task", "parameters": {}}}]
        result = provider.complete(messages=messages, tools=tools, agent="A", phase="execution", slot=1)
        exchange = provider.exchanges[0]
        self.assertEqual(seen, [exchange["request_text"]])
        self.assertEqual(json.loads(seen[0])["messages"], messages)
        self.assertEqual(json.loads(seen[0])["model"], CONFIG.model)
        self.assertEqual(exchange["raw_response"], raw)
        self.assertEqual(exchange["raw_response_sha256"], hashlib.sha256(raw.encode()).hexdigest())
        self.assertEqual(exchange["request_sha256"], hashlib.sha256(seen[0].encode()).hexdigest())
        self.assertEqual(result["tool_calls"], [{"name": "assign_task", "arguments": {"task_id": "skip"}}])

    def test_transport_failure_is_raised_once_without_retry_or_message_capture(self):
        attempts = []

        def failing(text):
            attempts.append(text)
            raise ConnectionError("https://example.invalid?key=SECRET")

        provider = LiveProvider(CONFIG, failing)
        with self.assertRaises(ConnectionError):
            provider.complete(messages=[], tools=[], agent="A", phase="preview", slot=1)
        self.assertEqual(len(attempts), 1)
        self.assertEqual(provider.exchanges[0]["transport_error"], "ConnectionError")
        self.assertNotIn("SECRET", json.dumps(provider.exchanges))

    def test_module_has_no_network_or_credential_imports(self):
        tree = ast.parse((Path(__file__).parent / "provider.py").read_text(encoding="utf-8"))
        imported = {alias.name.split(".")[0] for node in ast.walk(tree)
                    if isinstance(node, (ast.Import, ast.ImportFrom))
                    for alias in getattr(node, "names", [])}
        imported |= {node.module.split(".")[0] for node in ast.walk(tree)
                     if isinstance(node, ast.ImportFrom) and node.module}
        self.assertFalse(imported & {"socket", "http", "urllib", "requests", "httpx", "ssl", "os", "dotenv"})


class RunnerIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.cwd = Path.cwd()
        self.tmp = tempfile.TemporaryDirectory()
        os.chdir(self.tmp.name)
        self.addCleanup(self.restore)

    def restore(self):
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def run_live(self, condition, seed=1, mutate=None):
        env = make_environment(seed)
        transport = ScriptedTransport(env, mutate)
        root = Path(os.environ.get(
            "APART_SERAPH_ROOT", Path(__file__).resolve().parents[4] / ".runtime/SERAPH-1.0"
        ))
        runner = EpisodeRunner(env, condition=condition, episode_seed=seed,
                               provider=LiveProvider(CONFIG, transport),
                               seraph_root=root if condition == "G2" else None)
        return runner.run(), transport

    def test_g2_mocked_transport_canonical_inputs_ignore_raw_symbols(self):
        baseline, _ = self.run_live("G2")

        def change_symbols(index, raw):
            body = json.loads(raw)
            fn = body["choices"][0]["message"]["tool_calls"][0]["function"]
            if fn["name"] == "preview_task":
                args = json.loads(fn["arguments"])
                args["carrier_symbol"] = (args["carrier_symbol"] + 1) % 4
                fn["arguments"] = json.dumps(args)
            return json.dumps(body)

        changed, transport = self.run_live("G2", mutate=change_symbols)
        self.assertTrue(baseline["valid_for_comparison"])
        self.assertTrue(changed["valid_for_comparison"])
        self.assertEqual(len(transport.requests), 20)
        # Own histories legitimately contain own symbols; compare each actor's
        # first execution prompt, which contains the peer view, not own history.
        for left, right in zip(baseline["provider_inputs"], changed["provider_inputs"]):
            if left["phase"] == "execution":
                self.assertEqual(left["messages"][-1], right["messages"][-1])
        self.assertEqual(baseline["final_summary"], changed["final_summary"])

    def test_incomplete_completion_invalidates_g2_without_retry_or_assignment(self):
        for status in ("length", "content_filter"):
            def incomplete(index, raw):
                body = json.loads(raw)
                if index == 17:
                    body["choices"][0]["finish_reason"] = status
                return json.dumps(body)
            result, transport = self.run_live("G2", mutate=incomplete)
            self.assertFalse(result["valid_for_comparison"])
            self.assertEqual(len(transport.requests), 20)
            self.assertEqual(len([row for row in result["tool_results"]
                                  if row["phase"] == "execution"]), 3)
            self.assertEqual(result["final_summary"]["status"], "incomplete")
            self.assertEqual(result["final_summary"]["decisions_made"], 3)

    def run_scripted(self, condition, seed=1):
        env = make_environment(seed)
        return EpisodeRunner(env, condition=condition, episode_seed=seed, provider=ScriptedProvider(env)).run()

    def test_live_boundary_matches_scripted_contexts_and_native_results(self):
        for seed in (1, 2, 3):
            for condition in ("B0", "B1", "B2", "B2-S"):
                live, transport = self.run_live(condition, seed)
                scripted = self.run_scripted(condition, seed)
                self.assertTrue(live["valid_for_comparison"], live["failures"])
                self.assertEqual(live["provider_inputs"], scripted["provider_inputs"])
                self.assertEqual(live["final_summary"], scripted["final_summary"])
                untimed = [[{k: v for k, v in e.items() if k != "timestamp"} for e in r["host_events"]]
                           for r in (live, scripted)]
                self.assertEqual(untimed[0], untimed[1])
                self.assertEqual(len(transport.requests), 20)
                manifest = live["manifest"]
                self.assertEqual(manifest["inference_calls"], 20)
                self.assertFalse(manifest["scripted"])
                self.assertFalse(manifest["research_result"])
                self.assertEqual(manifest["provider_config_sha256"], CONFIG.digest)
                self.assertEqual([x["request_text"] for x in live["provider_exchanges"]], transport.requests)

    def test_invalid_live_response_invalidates_episode_without_retry(self):
        def corrupt(index, raw):
            if index == 6:
                return raw.replace('"arguments": "{', '"arguments": "{oops ')
            if index == 9:
                return raw.replace(CONFIG.model, "mock/fallback")
            return raw

        result, transport = self.run_live("B2", mutate=corrupt)
        self.assertFalse(result["valid_for_comparison"])
        self.assertEqual(len(transport.requests), 20)
        self.assertEqual(result["final_summary"]["status"], "complete")
        reasons = [x["invalid_reason"] for x in result["provider_exchanges"] if x["invalid_reason"]]
        self.assertEqual(len(reasons), 2)
        self.assertIn("model differs", reasons[1])

    def test_transport_failure_invalidates_episode_and_is_logged(self):
        env = make_environment(1)
        transport = ScriptedTransport(env)

        def flaky(text):
            if len(transport.requests) == 2:
                transport.requests.append(text)
                raise TimeoutError("timed out")
            return transport(text)

        runner = EpisodeRunner(env, condition="B2", episode_seed=1, provider=LiveProvider(CONFIG, flaky))
        result = runner.run()
        self.assertFalse(result["valid_for_comparison"])
        self.assertEqual(len(transport.requests), 20)
        self.assertEqual([x.get("transport_error") for x in result["provider_exchanges"]].count("TimeoutError"), 1)
        self.assertIn({"agent": runner.stage.agents[2], "phase": "preview", "error_type": "TimeoutError"},
                      result["failures"])


if __name__ == "__main__":
    unittest.main()
