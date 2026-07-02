"""Pydantic schemas for structured LLM output validation.

Each schema corresponds to the output of a specific hospital-workflow agent.
They are used with LangChain's ``with_structured_output`` so the LLM returns
validated, typed data instead of free-form text.
"""

from typing import Literal

from pydantic import BaseModel, Field


# ------------------------------------------------------------------
# Supervisor
# ------------------------------------------------------------------

class SupervisorDecision(BaseModel):
    """The routing decision made by the Supervisor agent."""

    next_agent: Literal[
        "admission",
        "insurance",
        "doctor",
        "lab",
        "pharmacy",
        "billing",
        "discharge",
        "FINISH",
    ] = Field(description="The next agent to route the workflow to, or FINISH to end.")
    reasoning: str = Field(description="Brief explanation of why this agent was chosen next.")


# ------------------------------------------------------------------
# Admission
# ------------------------------------------------------------------

class AdmissionOutput(BaseModel):
    """Structured output from the Admission agent."""

    symptoms: list[str] = Field(description="List of symptoms reported by the patient.")
    admission_type: str = Field(description="Type of admission — Emergency or Routine.")
    priority: str = Field(description="Triage priority — Low, Medium, High, or Critical.")
    assigned_department: str = Field(description="Hospital department the patient is assigned to.")
    status: str = Field(description="Current admission status — Pending or Admitted.")


# ------------------------------------------------------------------
# Insurance
# ------------------------------------------------------------------

class InsuranceOutput(BaseModel):
    """Structured output from the Insurance Verification agent."""

    provider: str = Field(description="Name of the insurance provider.")
    policy_number: str = Field(description="Insurance policy number.")
    verification_status: str = Field(description="Verification result — Pending, Approved, or Rejected.")
    coverage_percentage: float = Field(description="Percentage of costs covered by insurance.")
    remarks: str = Field(description="Additional notes or remarks about coverage.")


# ------------------------------------------------------------------
# Doctor
# ------------------------------------------------------------------

class DoctorOutput(BaseModel):
    """Structured output from the Doctor Consultation agent."""

    assigned_doctor: str = Field(description="Name of the doctor assigned to the patient.")
    diagnosis: str = Field(description="Preliminary or confirmed diagnosis.")
    treatment_plan: str = Field(description="Recommended treatment plan.")
    recommended_tests: list[str] = Field(description="Lab tests recommended by the doctor.")


# ------------------------------------------------------------------
# Lab
# ------------------------------------------------------------------

class LabOutput(BaseModel):
    """Structured output from the Lab agent."""

    ordered_tests: list[str] = Field(description="Tests that have been ordered.")
    completed_tests: list[str] = Field(description="Tests that have been completed.")
    reports: list[str] = Field(description="Summary reports for completed tests.")


# ------------------------------------------------------------------
# Pharmacy
# ------------------------------------------------------------------

class PharmacyOutput(BaseModel):
    """Structured output from the Pharmacy agent."""

    prescribed_medicines: list[str] = Field(description="List of prescribed medicines.")
    allergies: list[str] = Field(description="Known patient allergies to check against prescriptions.")
    pharmacist_notes: str = Field(description="Additional notes from the pharmacist.")


# ------------------------------------------------------------------
# Billing
# ------------------------------------------------------------------

class BillingOutput(BaseModel):
    """Structured output from the Billing agent."""

    estimated_cost: float = Field(description="Total estimated cost of treatment.")
    insurance_covered: float = Field(description="Amount covered by insurance.")
    patient_payable: float = Field(description="Amount the patient needs to pay.")
    payment_status: str = Field(description="Current payment status — Pending, Paid, or Partial.")


# ------------------------------------------------------------------
# Discharge
# ------------------------------------------------------------------

class DischargeOutput(BaseModel):
    """Structured output from the Discharge agent."""

    approved: bool = Field(description="Whether the discharge has been approved.")
    summary: str = Field(description="Discharge summary including treatment details.")
    follow_up_date: str = Field(description="Recommended follow-up appointment date.")
    instructions: str = Field(description="Post-discharge care instructions for the patient.")
