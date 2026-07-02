"""Supervisor Agent — workflow orchestrator.

The supervisor reads the entire HospitalState to decide which specialist
agent should run next.  It never performs domain work itself; it only
routes and tracks progress.

Writes: ``state["workflow"]``
"""

import json
from typing import Any

from langgraph.types import Command

from app.agents.base import BaseAgent
from app.state.hospital_state import HospitalState
from app.state.schemas import SupervisorDecision


# The canonical sequence of agents in the hospital workflow.
_AGENT_SEQUENCE = [
    "admission",
    "insurance",
    "doctor",
    "lab",
    "pharmacy",
    "billing",
    "discharge",
]


class SupervisorAgent(BaseAgent):
    """Orchestrates the hospital workflow by routing to specialist agents."""

    name = "supervisor"

    def run(self, state: HospitalState) -> Command[str]:
        """Decide which agent to invoke next, or finish the workflow."""

        workflow = state.get("workflow", {})
        completed_steps = workflow.get("completed_steps", [])

        # Build a concise summary of current state for the LLM
        context = {
            "patient": state.get("patient", {}),
            "admission": state.get("admission", {}),
            "insurance": state.get("insurance", {}),
            "doctor": state.get("doctor", {}),
            "lab": state.get("lab", {}),
            "pharmacy": state.get("pharmacy", {}),
            "billing": state.get("billing", {}),
            "discharge": state.get("discharge", {}),
            "completed_steps": completed_steps,
            "agent_sequence": _AGENT_SEQUENCE,
        }

        user_message = (
            "Here is the current hospital workflow state:\n"
            f"{json.dumps(context, indent=2, default=str)}\n\n"
            "Decide which agent should run next, or return FINISH if all "
            "steps are complete."
        )

        decision: SupervisorDecision = self.invoke_llm_structured(
            user_message=user_message,
            output_schema=SupervisorDecision,
        )

        print(f"\n🔀 Supervisor → {decision.next_agent} | Reason: {decision.reasoning}")

        # If the workflow is complete, route to END
        if decision.next_agent == "FINISH":
            return Command(
                goto="__end__",
                update={
                    "workflow": {
                        **workflow,
                        "next_agent": None,
                        "current_goal": "Workflow complete",
                    }
                },
            )

        # Otherwise, route to the chosen agent
        return Command(
            goto=decision.next_agent,
            update={
                "workflow": {
                    **workflow,
                    "next_agent": decision.next_agent,
                    "current_goal": f"Running {decision.next_agent} agent",
                }
            },
        )
