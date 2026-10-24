"""Deterministic candidate-carrier proofs against installed Terrarium."""

import copy
import os
import tempfile
import unittest
from pathlib import Path

from envs.dcops.jira_ticket.jira_ticket_env import JiraTicketEnvironment
from envs.dcops.jira_ticket.jira_ticket_tools import JiraTicketTools
from terrarium.blackboard import Megaboard, format_blackboard_events_for_prompt

from experiments.collusion.apart_2026.carrier import CarrierTools
from experiments.common.local_protocol import LocalCommunicationProtocol


class CarrierTest(unittest.TestCase):
    def setUp(self):
        self.cwd = Path.cwd()
        self.tmp = tempfile.TemporaryDirectory()
        os.chdir(self.tmp.name)
        self.addCleanup(self.restore)
        self.config = {
            "simulation": {"seed": 1, "tags": ["apart_gate0_scripted"]},
            "environment": {"name": "JiraTicketEnvironment", "max_tasks": 8, "assignment_filling": False},
            "communication_network": {"topology": "path", "num_agents": 4},
        }
        self.env = JiraTicketEnvironment(
            LocalCommunicationProtocol(config=self.config),
            self.config,
            None,
        )

    def restore(self):
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def test_native_schema_has_no_neutral_field(self):
        schema = JiraTicketTools(None).get_tools("execution")[0]["function"]["parameters"]
        self.assertEqual(set(schema["properties"]), {"task_id"})

    def test_one_two_four_selectable_peer_visible_encodings(self):
        sender, recipient = self.env.agent_names[:2]
        for bits in (0, 1, 2):
            for symbol in range(2**bits):
                board = Megaboard()
                board_id = board.add_blackboard([sender, recipient])
                tools = CarrierTools(board, capacity_bits=bits)
                schema = tools.get_tools("execution")[0]["function"]["parameters"]
                self.assertEqual(schema["properties"]["carrier_symbol"]["enum"], list(range(2**bits)))
                tools.handle_tool_call(
                    "assign_task",
                    sender,
                    {
                        "task_id": next(iter(self.env.tasks)),
                        "carrier_symbol": symbol,
                    },
                    phase="execution",
                    env_state=self.env.get_serializable_state(),
                )
                events = board.get(board_id, recipient, limit=None)
                self.assertEqual(events[-1]["payload"]["action_params"]["carrier_symbol"], symbol)
                rendered = format_blackboard_events_for_prompt(events)
                prompt = self.env.prompts._get_user_prompt_impl(
                    recipient,
                    {"phase": "execution"},
                    {str(board_id): rendered},
                )
                self.assertIn('"carrier_symbol":' + str(symbol), prompt)

    def test_native_state_rewards_and_results_equivalent_for_all_encodings(self):
        for task_id in [*self.env.tasks, "skip"]:
            sender = self.env.agent_names[0]
            initial = self.env.get_serializable_state()
            native = JiraTicketTools(None).handle_tool_call(
                "assign_task",
                sender,
                {"task_id": task_id},
                env_state=copy.deepcopy(initial),
            )
            expected_assignment = native["result"]["state_updates"]["assignment"]
            expected_rewards = self.env._rewards(expected_assignment)
            for bits in (0, 1, 2):
                for symbol in range(2**bits):
                    state = copy.deepcopy(initial)
                    response = CarrierTools(None, capacity_bits=bits).handle_tool_call(
                        "assign_task",
                        sender,
                        {"task_id": task_id, "carrier_symbol": symbol},
                        env_state=state,
                    )
                    self.assertEqual(response, native)
                    self.assertEqual(state, initial)
                    assignment = response["result"]["state_updates"]["assignment"]
                    self.assertEqual(self.env._rewards(assignment), expected_rewards)
                    self.env.assignment = {}
                    self.env.apply_state_updates(response["result"]["state_updates"])
                    self.assertEqual(self.env.assignment, expected_assignment)
                    self.env.assignment = {}

    def test_invalid_metadata_never_executes_or_exposes(self):
        sender, recipient = self.env.agent_names[:2]
        board = Megaboard()
        board_id = board.add_blackboard([sender, recipient])
        tools = CarrierTools(board, capacity_bits=1)
        for symbol in (-1, 2, True, "1", None):
            response = tools.handle_tool_call(
                "assign_task",
                sender,
                {
                    "task_id": "skip",
                    "carrier_symbol": symbol,
                },
                env_state=self.env.get_serializable_state(),
            )
            self.assertIn("error", response)
        self.assertEqual(board.get(board_id, recipient, limit=None), [])
        self.assertEqual(self.env.assignment, {})


if __name__ == "__main__":
    unittest.main()
