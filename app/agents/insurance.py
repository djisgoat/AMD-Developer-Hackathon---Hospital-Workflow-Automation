"""Insurance Agent — policy verification and coverage determination.

Reads:  ``state["patient"]``, ``state["admission"]``
Writes: ``state["insurance"]``
Tools:  verify_insurance, check_coverage
"""

import json
from typing import Any

from app.agents.base import BaseAgent
from app.state.hospital_state import HospitalState
from app.state.schemas import InsuranceOutput
from app.tools.insurance_tools import check_coverage, verify_insurance


class InsuranceAgent(BaseAgent):
    """Verifies the patient's insurance and determines coverage."""

    name = "insurance"
    tools = [verify_insurance, check_coverage]

    def run(self, state: HospitalState) -> dict[str, Any]:
        """Verify insurance policy and calculate coverage."""

        patient = state.get("patient", {})
        admission = state.get("admission", {})

        # Check if insurance info was provided in the initial state
        existing_insurance = state.get("insurance", {})
        policy_number = existing_insurance.get("policy_number", "")
        provider = existing_insurance.get("provider", "")

        if policy_number and provider:
            # Verify the insurance using tools
            verification = verify_insurance.invoke({
                "policy_number": policy_number,
                "provider": provider,
            })

            coverage = check_coverage.invoke({
                "policy_number": policy_number,
                "treatment_type": admission.get("admission_type", "Routine"),
            })
        else:
            verification = {"is_valid": False, "status": "No policy provided"}
            coverage = {"coverage_percentage": 0.0}

        # Let LLM reason about the verification and produce structured output
        user_message = (
            "Evaluate the insurance verification results and determine coverage:\n\n"
            f"Patient: {json.dumps(patient, indent=2, default=str)}\n"
            f"Admission: {json.dumps(admission, indent=2, default=str)}\n"
            f"Insurance info provided: provider={provider}, policy={policy_number}\n"
            f"Verification result: {json.dumps(verification, indent=2, default=str)}\n"
            f"Coverage result: {json.dumps(coverage, indent=2, default=str)}\n"
        )

        result: InsuranceOutput = self.invoke_llm_structured(
            user_message=user_message,
            output_schema=InsuranceOutput,
        )

        print(f"\n🛡️  Insurance Agent:")
        print(f"   Provider: {result.provider}")
        print(f"   Status: {result.verification_status}")
        print(f"   Coverage: {result.coverage_percentage}%")

        workflow = state.get("workflow", {})
        completed = workflow.get("completed_steps", [])

        return {
            "insurance": result.model_dump(),
            "workflow": {
                **workflow,
                "completed_steps": completed + ["insurance"],
            },
        }
