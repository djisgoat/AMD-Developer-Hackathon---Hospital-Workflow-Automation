"""Hospital Automation — Agentic AI Orchestration Platform.

Entry point that builds the LangGraph workflow, feeds a sample patient,
and runs the full admission-to-discharge pipeline.
"""

import json

from dotenv import load_dotenv

load_dotenv()

from app.graph.workflow import build_workflow


def print_banner() -> None:
    """Print a startup banner."""
    print("=" * 64)
    print("  🏥  Hospital Automation — AI Workflow Orchestration")
    print("=" * 64)


def print_final_state(state: dict) -> None:
    """Pretty-print the final HospitalState."""
    print("\n" + "=" * 64)
    print("  📋  FINAL WORKFLOW STATE")
    print("=" * 64)

    sections = [
        ("Patient", "patient"),
        ("Admission", "admission"),
        ("Insurance", "insurance"),
        ("Doctor", "doctor"),
        ("Lab", "lab"),
        ("Pharmacy", "pharmacy"),
        ("Billing", "billing"),
        ("Discharge", "discharge"),
        ("Workflow", "workflow"),
    ]

    for title, key in sections:
        data = state.get(key, {})
        print(f"\n── {title} {'─' * (50 - len(title))}")
        if isinstance(data, dict):
            for k, v in data.items():
                print(f"   {k}: {v}")
        else:
            print(f"   {data}")

    print("\n" + "=" * 64)
    print("  ✅  Workflow Complete!")
    print("=" * 64)


def main() -> None:
    """Run the full hospital workflow with a sample patient."""

    print_banner()

    # ── Build the LangGraph workflow ─────────────────────────────
    workflow = build_workflow()

    # ── Sample patient input ─────────────────────────────────────
    initial_state = {
        "patient": {
            "patient_id": "",
            "aadhaar_number": "1234-5678-9012",
            "name": "Rajesh Kumar",
            "age": 45,
            "gender": "Male",
            "phone_number": "+91-9876543210",
        },
        "admission": {
            "symptoms": ["chest pain", "shortness of breath", "dizziness"],
            "admission_type": "",
            "priority": "",
            "assigned_department": None,
            "status": "Pending",
        },
        "insurance": {
            "provider": "Star Health Insurance",
            "policy_number": "POL-2024-78432",
            "verification_status": "Pending",
            "coverage_percentage": 0.0,
            "remarks": "",
        },
        "doctor": {
            "assigned_doctor": None,
            "diagnosis": "",
            "treatment_plan": "",
            "recommended_tests": [],
        },
        "lab": {
            "ordered_tests": [],
            "completed_tests": [],
            "reports": [],
        },
        "pharmacy": {
            "prescribed_medicines": [],
            "allergies": ["Penicillin"],
            "pharmacist_notes": "",
        },
        "billing": {
            "estimated_cost": 0.0,
            "insurance_covered": 0.0,
            "patient_payable": 0.0,
            "payment_status": "Pending",
        },
        "discharge": {
            "approved": False,
            "summary": "",
            "follow_up_date": "",
            "instructions": "",
        },
        "workflow": {
            "current_goal": "Begin patient workflow",
            "next_agent": None,
            "completed_steps": [],
        },
        "messages": [],
        "error": None,
    }

    print(f"\n📥 Patient: {initial_state['patient']['name']}")
    print(f"   Symptoms: {', '.join(initial_state['admission']['symptoms'])}")
    print(f"   Insurance: {initial_state['insurance']['provider']} ({initial_state['insurance']['policy_number']})")
    print(f"\n{'─' * 64}")
    print("   Starting workflow...\n")

    # ── Execute the workflow ─────────────────────────────────────
    final_state = workflow.invoke(initial_state)

    # ── Display results ──────────────────────────────────────────
    print_final_state(final_state)


if __name__ == "__main__":
    main()
