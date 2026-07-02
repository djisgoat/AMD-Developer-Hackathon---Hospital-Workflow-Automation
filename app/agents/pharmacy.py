"""Pharmacy Agent — medication management and dispensing.

Reads:  ``state["doctor"]``, ``state["patient"]``, ``state["lab"]``
Writes: ``state["pharmacy"]``
Tools:  check_drug_interactions, dispense_medication
"""

import json
from typing import Any

from app.agents.base import BaseAgent
from app.state.hospital_state import HospitalState
from app.state.schemas import PharmacyOutput
from app.tools.pharmacy_tools import check_drug_interactions, dispense_medication


class PharmacyAgent(BaseAgent):
    """Validates prescriptions, checks interactions, dispenses medication."""

    name = "pharmacy"
    tools = [check_drug_interactions, dispense_medication]

    def run(self, state: HospitalState) -> dict[str, Any]:
        """Check drug safety, dispense medicines, provide notes."""

        doctor = state.get("doctor", {})
        patient = state.get("patient", {})
        lab = state.get("lab", {})

        # Let the LLM extract medicines from the treatment plan
        user_message = (
            "Based on the doctor's treatment plan, determine the medicines "
            "to prescribe and check for any safety concerns.\n\n"
            f"Patient: {json.dumps(patient, indent=2, default=str)}\n"
            f"Doctor: {json.dumps(doctor, indent=2, default=str)}\n"
            f"Lab results: {json.dumps(lab, indent=2, default=str)}\n"
        )

        result: PharmacyOutput = self.invoke_llm_structured(
            user_message=user_message,
            output_schema=PharmacyOutput,
        )

        # Check drug interactions using the tool
        if result.prescribed_medicines:
            interaction_check = check_drug_interactions.invoke({
                "medicines": result.prescribed_medicines,
                "allergies": result.allergies,
            })

            # Dispense the medications
            dispense_result = dispense_medication.invoke({
                "medicines": result.prescribed_medicines,
                "patient_id": patient.get("patient_id", "UNKNOWN"),
            })

            print(f"\n💊 Pharmacy Agent:")
            print(f"   Medicines: {', '.join(result.prescribed_medicines)}")
            print(f"   Interactions: {'⚠️ Found' if interaction_check.get('interactions_found') else '✅ None'}")
            print(f"   Dispensing ID: {dispense_result.get('dispensing_id', 'N/A')}")
        else:
            print("\n💊 Pharmacy Agent: No medicines to dispense.")

        workflow = state.get("workflow", {})
        completed = workflow.get("completed_steps", [])

        return {
            "pharmacy": result.model_dump(),
            "workflow": {
                **workflow,
                "completed_steps": completed + ["pharmacy"],
            },
        }
