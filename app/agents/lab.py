"""Lab Agent — test ordering and result management.

Reads:  ``state["doctor"]`` (recommended_tests)
Writes: ``state["lab"]``
Tools:  order_tests, fetch_lab_results
"""

import json
from typing import Any

from app.agents.base import BaseAgent
from app.state.hospital_state import HospitalState
from app.state.schemas import LabOutput
from app.tools.lab_tools import fetch_lab_results, order_tests


class LabAgent(BaseAgent):
    """Orders lab tests and retrieves results."""

    name = "lab"
    tools = [order_tests, fetch_lab_results]

    def run(self, state: HospitalState) -> dict[str, Any]:
        """Order recommended tests, fetch results, compile reports."""

        doctor = state.get("doctor", {})
        patient = state.get("patient", {})
        recommended_tests = doctor.get("recommended_tests", [])

        if not recommended_tests:
            print("\n🔬 Lab Agent: No tests recommended — skipping.")
            workflow = state.get("workflow", {})
            completed = workflow.get("completed_steps", [])
            return {
                "lab": {
                    "ordered_tests": [],
                    "completed_tests": [],
                    "reports": [],
                },
                "workflow": {
                    **workflow,
                    "completed_steps": completed + ["lab"],
                },
            }

        patient_id = patient.get("patient_id", "UNKNOWN")

        # Order the tests
        order_result = order_tests.invoke({
            "test_names": recommended_tests,
            "patient_id": patient_id,
        })

        order_id = order_result.get("order_id", "ORD-UNKNOWN")

        # Fetch results (simulated)
        lab_results = fetch_lab_results.invoke({
            "order_id": order_id,
            "test_names": recommended_tests,
        })

        # Let LLM compile structured reports from raw results
        user_message = (
            "Compile lab reports from the following test results:\n\n"
            f"Order ID: {order_id}\n"
            f"Tests ordered: {json.dumps(recommended_tests, default=str)}\n"
            f"Raw results: {json.dumps(lab_results, indent=2, default=str)}\n"
        )

        result: LabOutput = self.invoke_llm_structured(
            user_message=user_message,
            output_schema=LabOutput,
        )

        print(f"\n🔬 Lab Agent:")
        print(f"   Ordered: {', '.join(result.ordered_tests)}")
        print(f"   Completed: {', '.join(result.completed_tests)}")
        print(f"   Reports: {len(result.reports)} report(s) generated")

        workflow = state.get("workflow", {})
        completed = workflow.get("completed_steps", [])

        return {
            "lab": result.model_dump(),
            "workflow": {
                **workflow,
                "completed_steps": completed + ["lab"],
            },
        }
