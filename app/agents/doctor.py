"""Doctor Agent — diagnosis, treatment planning, and test recommendations.

Reads:  ``state["patient"]``, ``state["admission"]``, ``state["insurance"]``
Writes: ``state["doctor"]``
Tools:  lookup_doctor_availability
"""

import json
from typing import Any

from app.agents.base import BaseAgent
from app.state.hospital_state import HospitalState
from app.state.schemas import DoctorOutput
from app.tools.doctor_tools import lookup_doctor_availability


class DoctorAgent(BaseAgent):
    """Assigns a doctor, creates diagnosis and treatment plan."""

    name = "doctor"
    tools = [lookup_doctor_availability]

    def run(self, state: HospitalState) -> dict[str, Any]:
        """Assign doctor, diagnose, plan treatment, recommend tests."""

        patient = state.get("patient", {})
        admission = state.get("admission", {})
        insurance = state.get("insurance", {})

        department = admission.get("assigned_department", "General Medicine")

        # Look up an available doctor for this department
        doctor_info = lookup_doctor_availability.invoke({
            "department": department,
        })

        user_message = (
            "You are consulting on the following patient. Provide a diagnosis, "
            "treatment plan, and any recommended lab tests.\n\n"
            f"Patient: {json.dumps(patient, indent=2, default=str)}\n"
            f"Admission: {json.dumps(admission, indent=2, default=str)}\n"
            f"Insurance: {json.dumps(insurance, indent=2, default=str)}\n"
            f"Available doctor: {json.dumps(doctor_info, indent=2, default=str)}\n"
        )

        result: DoctorOutput = self.invoke_llm_structured(
            user_message=user_message,
            output_schema=DoctorOutput,
        )

        # Override assigned doctor with the one found by the tool
        assigned_doctor = doctor_info.get("doctor_name", result.assigned_doctor)

        print(f"\n👨‍⚕️ Doctor Agent:")
        print(f"   Doctor: Dr. {assigned_doctor}")
        print(f"   Diagnosis: {result.diagnosis}")
        print(f"   Tests: {', '.join(result.recommended_tests) or 'None'}")

        workflow = state.get("workflow", {})
        completed = workflow.get("completed_steps", [])

        return {
            "doctor": {
                "assigned_doctor": assigned_doctor,
                "diagnosis": result.diagnosis,
                "treatment_plan": result.treatment_plan,
                "recommended_tests": result.recommended_tests,
            },
            "workflow": {
                **workflow,
                "completed_steps": completed + ["doctor"],
            },
        }
