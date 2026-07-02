"""Admission Agent — patient triage and department assignment.

Reads:  ``state["patient"]``
Writes: ``state["admission"]``
Tools:  generate_patient_id, assign_department
"""

import json
from typing import Any

from app.agents.base import BaseAgent
from app.state.hospital_state import HospitalState
from app.state.schemas import AdmissionOutput
from app.tools.admission_tools import assign_department, generate_patient_id


class AdmissionAgent(BaseAgent):
    """Triages the patient and assigns them to a department."""

    name = "admission"
    tools = [generate_patient_id, assign_department]

    def run(self, state: HospitalState) -> dict[str, Any]:
        """Triage symptoms, determine priority, assign department."""

        patient = state.get("patient", {})

        # Use the tool to generate a patient ID if not yet assigned
        patient_id = patient.get("patient_id", "")
        if not patient_id:
            patient_id = generate_patient_id.invoke({"name": patient.get("name", "Unknown")})

        # Build context for the LLM
        user_message = (
            "Triage the following patient and determine admission details:\n"
            f"{json.dumps(patient, indent=2, default=str)}\n\n"
            f"Patient symptoms context from intake: "
            f"{json.dumps(state.get('admission', {}).get('symptoms', []), default=str)}"
        )

        result: AdmissionOutput = self.invoke_llm_structured(
            user_message=user_message,
            output_schema=AdmissionOutput,
        )

        # Optionally use the assign_department tool for validation
        dept_info = assign_department.invoke({
            "symptoms": result.symptoms,
            "priority": result.priority,
        })

        print(f"\n🏥 Admission Agent:")
        print(f"   Priority: {result.priority}")
        print(f"   Department: {dept_info['department']}")
        print(f"   Ward: {dept_info['ward_type']} | Bed: {dept_info['bed_number']}")

        # Update patient with generated ID
        updated_patient = {**patient, "patient_id": patient_id}

        # Mark this step as completed
        workflow = state.get("workflow", {})
        completed = workflow.get("completed_steps", [])

        return {
            "patient": updated_patient,
            "admission": {
                "symptoms": result.symptoms,
                "admission_type": result.admission_type,
                "priority": result.priority,
                "assigned_department": dept_info["department"],
                "status": "Admitted",
            },
            "workflow": {
                **workflow,
                "completed_steps": completed + ["admission"],
            },
        }
