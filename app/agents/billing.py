"""Billing Agent — cost calculation and payment processing.

Reads:  ``state["doctor"]``, ``state["lab"]``, ``state["pharmacy"]``, ``state["insurance"]``
Writes: ``state["billing"]``
Tools:  calculate_costs, process_payment
"""

import json
from typing import Any

from app.agents.base import BaseAgent
from app.state.hospital_state import HospitalState
from app.state.schemas import BillingOutput
from app.tools.billing_tools import calculate_costs, process_payment


class BillingAgent(BaseAgent):
    """Calculates total costs, applies insurance, processes payment."""

    name = "billing"
    tools = [calculate_costs, process_payment]

    def run(self, state: HospitalState) -> dict[str, Any]:
        """Calculate costs, apply insurance coverage, determine payable."""

        doctor = state.get("doctor", {})
        lab = state.get("lab", {})
        pharmacy = state.get("pharmacy", {})
        insurance = state.get("insurance", {})

        # Build a services dict for the cost calculator
        services = {
            "consultation": doctor.get("assigned_doctor", "General"),
            "lab_tests": lab.get("completed_tests", []),
            "medicines": pharmacy.get("prescribed_medicines", []),
            "room_charges": state.get("admission", {}).get("assigned_department", "General"),
        }

        # Calculate itemized costs using the tool
        cost_result = calculate_costs.invoke({"services": services})

        grand_total = cost_result.get("grand_total", 0.0)
        coverage_pct = insurance.get("coverage_percentage", 0.0)
        insurance_covered = round(grand_total * (coverage_pct / 100), 2)
        patient_payable = round(grand_total - insurance_covered, 2)

        # Let LLM produce a clean structured billing output
        user_message = (
            "Generate the billing summary based on the following data:\n\n"
            f"Services: {json.dumps(services, indent=2, default=str)}\n"
            f"Cost breakdown: {json.dumps(cost_result, indent=2, default=str)}\n"
            f"Insurance coverage: {coverage_pct}%\n"
            f"Insurance amount: ₹{insurance_covered}\n"
            f"Patient payable: ₹{patient_payable}\n"
        )

        result: BillingOutput = self.invoke_llm_structured(
            user_message=user_message,
            output_schema=BillingOutput,
        )

        # Process payment (simulated)
        payment_result = process_payment.invoke({
            "amount": result.patient_payable,
            "method": "UPI",
        })

        print(f"\n💰 Billing Agent:")
        print(f"   Total Cost: ₹{result.estimated_cost}")
        print(f"   Insurance Covers: ₹{result.insurance_covered}")
        print(f"   Patient Pays: ₹{result.patient_payable}")
        print(f"   Payment: {payment_result.get('status', 'Unknown')}")

        workflow = state.get("workflow", {})
        completed = workflow.get("completed_steps", [])

        return {
            "billing": {
                "estimated_cost": result.estimated_cost,
                "insurance_covered": result.insurance_covered,
                "patient_payable": result.patient_payable,
                "payment_status": payment_result.get("status", result.payment_status),
            },
            "workflow": {
                **workflow,
                "completed_steps": completed + ["billing"],
            },
        }
