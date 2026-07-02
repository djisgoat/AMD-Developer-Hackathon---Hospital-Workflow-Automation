"""Discharge Agent — final step: summary, instructions, follow-up.

Reads:  entire state
Writes: ``state["discharge"]``
Tools:  generate_discharge_summary
"""

import json
from typing import Any

from app.agents.base import BaseAgent
from app.state.hospital_state import HospitalState
from app.state.schemas import DischargeOutput
from app.tools.discharge_tools import generate_discharge_summary


class DischargeAgent(BaseAgent):
    """Produces the discharge summary and post-care instructions."""

    name = "discharge"
    tools = [generate_discharge_summary]

    def run(self, state: HospitalState) -> dict[str, Any]:
        """Compile full discharge summary with follow-up plan."""

        patient = state.get("patient", {})
        admission = state.get("admission", {})
        doctor = state.get("doctor", {})
        lab = state.get("lab", {})
        pharmacy = state.get("pharmacy", {})
        billing = state.get("billing", {})

        # Let the LLM decide on discharge details
        user_message = (
            "Review the complete patient journey and produce a discharge plan:\n\n"
            f"Patient: {json.dumps(patient, indent=2, default=str)}\n"
            f"Admission: {json.dumps(admission, indent=2, default=str)}\n"
            f"Doctor: {json.dumps(doctor, indent=2, default=str)}\n"
            f"Lab: {json.dumps(lab, indent=2, default=str)}\n"
            f"Pharmacy: {json.dumps(pharmacy, indent=2, default=str)}\n"
            f"Billing: {json.dumps(billing, indent=2, default=str)}\n"
        )

        result: DischargeOutput = self.invoke_llm_structured(
            user_message=user_message,
            output_schema=DischargeOutput,
        )

        # Use the tool to generate the formal discharge document
        summary_doc = generate_discharge_summary.invoke({
            "patient_name": patient.get("name", "Unknown"),
            "diagnosis": doctor.get("diagnosis", "N/A"),
            "treatment": doctor.get("treatment_plan", "N/A"),
            "follow_up_date": result.follow_up_date,
        })

        print(f"\n🚪 Discharge Agent:")
        print(f"   Approved: {'✅ Yes' if result.approved else '❌ No'}")
        print(f"   Follow-up: {result.follow_up_date}")
        print(f"   Summary ID: {summary_doc.get('summary_id', 'N/A')}")

        workflow = state.get("workflow", {})
        completed = workflow.get("completed_steps", [])

        return {
            "discharge": {
                "approved": result.approved,
                "summary": result.summary,
                "follow_up_date": result.follow_up_date,
                "instructions": result.instructions,
            },
            "workflow": {
                **workflow,
                "completed_steps": completed + ["discharge"],
            },
        }
