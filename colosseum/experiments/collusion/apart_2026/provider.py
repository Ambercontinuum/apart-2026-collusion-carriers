"""Live-provider boundary for the D1 runner. Transport is injected; nothing here opens a connection.

One request per turn and one strict parse per response: no retry, no fallback model, no padding.
The exact request text sent and the exact response text received are kept in `exchanges`.
"""

import copy
from dataclasses import asdict, dataclass
import hashlib
import json
import math


@dataclass(frozen=True)
class ProviderConfig:
    model: str
    temperature: float
    max_tokens: int
    tool_choice: str = "required"
    seed: int | None = None

    def to_wire(self):
        return asdict(self)

    @property
    def digest(self):
        return _sha256(json.dumps(self.to_wire(), sort_keys=True, separators=(",", ":")))


def _sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _unique_object(pairs):
    keys = [key for key, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate JSON key")
    return dict(pairs)


def _reject_constant(name):
    raise ValueError(f"non-finite JSON constant {name}")


def _finite_float(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError("non-finite JSON number")
    return value


def strict_loads(text):
    """json.loads without duplicate keys or non-finite numbers, which would make parsing ambiguous."""
    return json.loads(
        text, object_pairs_hook=_unique_object, parse_constant=_reject_constant, parse_float=_finite_float
    )


def parse_response(raw, *, model):
    """Return (calls, None) or ([], reason). Arguments must arrive as a JSON string and are parsed once."""
    try:
        body = strict_loads(raw)
    except (TypeError, ValueError) as exc:
        return [], f"response is not strict JSON: {exc}"
    if not isinstance(body, dict):
        return [], "response must be a JSON object"
    if body.get("model") != model:
        return [], "response model differs from configured model"
    choices = body.get("choices")
    if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
        return [], "exactly one choice required"
    if choices[0].get("finish_reason") != "tool_calls":
        return [], "completed tool_calls finish reason required"
    message = choices[0].get("message")
    tool_calls = message.get("tool_calls") if isinstance(message, dict) else None
    if not isinstance(tool_calls, list) or not tool_calls:
        return [], "no tool call"
    calls = []
    for item in tool_calls:
        function = item.get("function") if isinstance(item, dict) else None
        if not isinstance(function, dict) or item.get("type") != "function":
            return [], "tool call must be a function call"
        name, arguments = function.get("name"), function.get("arguments")
        if type(name) is not str or type(arguments) is not str:
            return [], "tool call needs a string name and JSON-string arguments"
        try:
            parsed = strict_loads(arguments)
        except ValueError as exc:
            return [], f"tool arguments are not strict JSON: {exc}"
        if not isinstance(parsed, dict):
            return [], "tool arguments must be a JSON object"
        calls.append({"name": name, "arguments": parsed})
    return calls, None


class LiveProvider:
    """Maps the runner's captured request to one transport call. `transport(request_text) -> response_text`."""

    def __init__(self, config, transport):
        self.config = config
        self.transport = transport
        self.exchanges = []

    @property
    def transport_attempts(self):
        return len(self.exchanges)

    def request_text(self, messages, tools):
        payload = {
            "model": self.config.model,
            "messages": copy.deepcopy(messages),
            "tools": copy.deepcopy(tools),
            "tool_choice": self.config.tool_choice,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "n": 1,
        }
        if self.config.seed is not None:
            payload["seed"] = self.config.seed
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)

    def complete(self, *, messages, tools, agent, phase, slot):
        request = self.request_text(messages, tools)
        exchange = {
            "index": len(self.exchanges),
            "agent": agent,
            "phase": phase,
            "slot": slot,
            "request_text": request,
            "request_sha256": _sha256(request),
        }
        self.exchanges.append(exchange)
        try:
            raw = self.transport(request)
        except Exception as exc:
            # Error type only: transport messages can carry endpoints or credentials.
            exchange["transport_error"] = type(exc).__name__
            raise
        if type(raw) is not str:
            exchange["transport_error"] = "non-text response"
            raise TypeError("transport must return response text")
        calls, reason = parse_response(raw, model=self.config.model)
        exchange.update(raw_response=raw, raw_response_sha256=_sha256(raw), invalid_reason=reason)
        return {"tool_calls": calls, "raw_response_sha256": exchange["raw_response_sha256"], "invalid_reason": reason}
