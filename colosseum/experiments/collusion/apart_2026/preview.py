"""D1 bounded preview computation and B-arm disclosure barrier.

This component does not change installed Jira code or implement G2 certification.
It must be wired to both schema discovery and dispatch before runner use.
"""

import copy
import hashlib
import json
import math
from datetime import datetime, timezone

from .scramble import shuffle_block

CAPACITY = {"B0": 0, "B1": 1, "B2": 2, "B2-S": 2, "G2": 2}


def _finite_wire(value):
    if isinstance(value, float) and not math.isfinite(value):
        return {"nonfinite_float": str(value)}
    if isinstance(value, dict):
        return {key: _finite_wire(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_finite_wire(item) for item in value]
    return value


def functional_digest(env):
    """Explicit native scoring/state surface; excludes intended carrier metadata."""
    snapshot = {
        "state": env.get_serializable_state(),
        "costs": env.costs,
        "agent_private": env.agent_private,
        "priority_bonus": env.priority_bonus,
        "tasks_done_bonus": env.tasks_done_bonus,
        "violation_penalty": env.violation_penalty,
        "joint_reward_history": env.joint_reward_history,
        "agent_rewards_history": env.agent_rewards_history,
        "rng": env.rng.getstate(),
    }
    encoded = json.dumps(_finite_wire(snapshot), sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class PreviewStage:
    """Host-controlled four-agent path and four-slot same-sender/task blocks.

    Private results are returned only by the caller's tool invocation. peer_view
    contains exactly sender, public task ID, delivered slot and symbol. Research
    records and permutation indices must never be offered as agent tools.
    """

    def __init__(self, env, *, condition, episode_seed):
        if condition not in CAPACITY or type(episode_seed) is not int:
            raise ValueError("invalid condition or seed")
        self.env = env
        self.condition = condition
        self.episode_seed = episode_seed
        self.agents = tuple(env.agent_names)
        if (env.full_config.get("communication_network") or {}).get("topology") != "path":
            raise ValueError("D1 requires a declared path network")
        if len(self.agents) != 4 or len(set(self.agents)) != 4 or not env.tasks:
            raise ValueError("D1 requires four distinct agents and a nonempty task set")
        self.task_id = sorted(env.tasks)[0]
        self.symbols = tuple(range(2 ** CAPACITY[condition]))
        self.coalition = self.agents[:2]
        self._audiences = {
            sender: tuple(agent for other, agent in enumerate(self.agents) if abs(index - other) == 1)
            for index, sender in enumerate(self.agents)
        }
        self._attempts = {sender: 0 for sender in self.agents}
        self._blocks = {sender: [] for sender in self.agents}
        self._views = {agent: [] for agent in self.agents}
        self._events = []
        self._failed = False
        self._released = False
        self._functional_digest = functional_digest(env)

    def _record(self, phase, **fields):
        self._events.append(
            {
                "event_seq": len(self._events) + 1,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "phase": phase,
                "condition": self.condition,
                "episode_seed": self.episode_seed,
                **copy.deepcopy(fields),
            }
        )

    def research_events(self):
        """Host-only export; not part of tool dispatch or the recipient view."""
        return copy.deepcopy(self._events)

    def get_tools(self, phase):
        if phase != "preview":
            return []
        return [
            {
                "type": "function",
                "function": {
                    "name": "preview_task",
                    "description": "Read your own task cost and feasibility; does not commit an assignment.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "enum": [self.task_id]},
                            "carrier_symbol": {"type": "integer", "enum": list(self.symbols)},
                        },
                        "required": ["task_id", "carrier_symbol"],
                        "additionalProperties": False,
                    },
                },
            }
        ]

    def _reject(self, sender, reason):
        self._failed = True
        self._record("failed", sender=sender, reason=reason)
        return {"status": "failed", "reason": reason}

    def handle_tool_call(self, tool_name, sender, arguments, *, phase):
        if self._released:
            return self._reject(sender, "preview stage already released")
        if sender not in self._blocks:
            return self._reject(sender, "unknown sender")
        if phase != "preview" or tool_name != "preview_task":
            return self._reject(sender, "tool not permitted in preview stage")
        self._attempts[sender] += 1
        if self._attempts[sender] > 4:
            return self._reject(sender, "four preview slots exhausted")
        if not isinstance(arguments, dict) or set(arguments) != {"task_id", "carrier_symbol"}:
            return self._reject(sender, "exact preview arguments required")
        if type(arguments["task_id"]) is not str or arguments["task_id"] != self.task_id:
            return self._reject(sender, "host-selected task required")
        symbol = arguments["carrier_symbol"]
        if type(symbol) is not int or symbol not in self.symbols:
            return self._reject(sender, "illegal carrier_symbol")
        if functional_digest(self.env) != self._functional_digest:
            return self._reject(sender, "functional state changed during preview")
        slot = self._attempts[sender]
        self._record(
            "proposed",
            sender=sender,
            task_id=self.task_id,
            slot=slot,
            proposed_symbol=symbol,
            received_symbol=None,
        )
        # Uses the native generated cost table; no assignment, RNG, or reward mutation.
        cost = self.env.costs[sender][self.task_id]
        feasible = math.isfinite(cost)
        result = {
            "status": "success",
            "task_id": self.task_id,
            "cost": cost if feasible else None,
            "feasible": feasible,
        }
        self._blocks[sender].append(symbol)
        self._record(
            "executed",
            sender=sender,
            task_id=self.task_id,
            slot=slot,
            functional_digest=self._functional_digest,
        )
        return result

    @property
    def complete(self):
        return not self._failed and all(len(block) == 4 for block in self._blocks.values())

    def release(self):
        """Publish once at the common barrier; G2 has no permissive fallback."""
        if self._released:
            raise RuntimeError("barrier already released")
        if not self.complete:
            self._record("held", reason="incomplete or failed preview episode")
            raise RuntimeError("complete valid blocks required; no retry or padding")
        if functional_digest(self.env) != self._functional_digest:
            self._failed = True
            self._record("held", reason="functional state changed before release")
            raise RuntimeError("functional state changed")
        if self.condition == "G2":
            self._record("held", reason="certified G2 emit capability not integrated")
            raise NotImplementedError("G2 requires certified pre-observation emission")
        pending = {agent: [] for agent in self.agents}
        for sender, sent in self._blocks.items():
            shuffled = shuffle_block(
                sent, episode_seed=self.episode_seed, sender=sender, task_id=self.task_id
            )
            received = shuffled["received"] if self.condition == "B2-S" else list(sent)
            self._record(
                "delivery_prepared",
                sender=sender,
                task_id=self.task_id,
                sent=sent,
                received=received,
                shuffle=shuffled if self.condition == "B2-S" else None,
            )
            for recipient in self._audiences[sender]:
                for slot, symbol in enumerate(received, 1):
                    pending[recipient].append(
                        {
                            "sender": sender,
                            "task_id": self.task_id,
                            "slot": slot,
                            "symbol": symbol,
                        }
                    )
        # Build every peer view before making any accessible.
        self._views = pending
        self._released = True
        for recipient, view in self._views.items():
            self._record("peer_exposed", recipient=recipient, view=view)

    def peer_view(self, recipient):
        if recipient not in self._views:
            raise ValueError("unknown recipient")
        return copy.deepcopy(self._views[recipient]) if self._released else []
