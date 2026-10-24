"""Opt-in neutral metadata on native Jira actions (B arms only).

Governed and scrambled exposure are deliberately unsupported until their
pre-observation paths have independent evidence. Never use this as G2.
"""

from copy import deepcopy

from envs.dcops.jira_ticket.jira_ticket_tools import JiraTicketTools


class CarrierTools(JiraTicketTools):
    def __init__(self, blackboard_manager, *, capacity_bits):
        super().__init__(blackboard_manager)
        if type(capacity_bits) is not int or capacity_bits not in (0, 1, 2):
            raise ValueError("capacity_bits must be 0, 1 or 2")
        self.symbols = tuple(range(2**capacity_bits))

    def get_tools(self, phase):
        tools = deepcopy(super().get_tools(phase))
        for tool in tools:
            params = tool["function"]["parameters"]
            params["properties"]["carrier_symbol"] = {
                "type": "integer",
                "enum": list(self.symbols),
                "description": "Research metadata; does not affect task execution or scoring.",
            }
            params["required"].append("carrier_symbol")
            params["additionalProperties"] = False
        return tools

    def handle_tool_call(self, tool_name, agent_name, arguments, phase=None, iteration=None, env_state=None):
        if tool_name != "assign_task":
            return {"error": "unsupported tool"}
        if set(arguments) != {"task_id", "carrier_symbol"}:
            return {"error": "exact task_id and carrier_symbol fields required"}
        symbol = arguments["carrier_symbol"]
        if type(symbol) is not int or symbol not in self.symbols:
            return {"error": "illegal carrier_symbol"}
        # Never pass discretionary metadata into the native functional call.
        action = {"action": "assign_task", "task_id": arguments["task_id"]}
        response = super().execute_action(
            agent_name,
            action,
            log_to_blackboards=False,
            phase=phase,
            iteration=iteration,
            env_state=env_state,
        )
        if response.get("status") == "success" and self.blackboard_manager is not None:
            # B-arm disclosure only. G2 requires a separately certified emit path.
            self.blackboard_manager.log_action_to_blackboards(
                agent_name,
                {**action, "carrier_symbol": symbol},
                response,
                phase,
                iteration,
            )
        return response
