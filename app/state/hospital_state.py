from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


# ------------------------
# Patient Information
# ------------------------

class Patient(TypedDict):
    patient_id: str
    aadhaar_number: str | None
    name: str
    age: int
    gender: str
    phone_number: str


# ------------------------
# Admission
# ------------------------

class Admission(TypedDict):
    symptoms: list[str]
    admission_type: str          # Emergency / Routine
    priority: str                # Low / Medium / High / Critical
    assigned_department: str | None
    status: str                  # Pending / Admitted


# ------------------------
# Insurance
# ------------------------

class Insurance(TypedDict):
    provider: str
    policy_number: str
    verification_status: str     # Pending / Approved / Rejected
    coverage_percentage: float
    remarks: str


# ------------------------
# Doctor
# ------------------------

class Doctor(TypedDict):
    assigned_doctor: str | None
    diagnosis: str
    treatment_plan: str
    recommended_tests: list[str]


# ------------------------
# Lab
# ------------------------

class Lab(TypedDict):
    ordered_tests: list[str]
    completed_tests: list[str]
    reports: list[str]


# ------------------------
# Pharmacy
# ------------------------

class Pharmacy(TypedDict):
    prescribed_medicines: list[str]
    allergies: list[str]
    pharmacist_notes: str


# ------------------------
# Billing
# ------------------------

class Billing(TypedDict):
    estimated_cost: float
    insurance_covered: float
    patient_payable: float
    payment_status: str


# ------------------------
# Discharge
# ------------------------

class Discharge(TypedDict):
    approved: bool
    summary: str
    follow_up_date: str
    instructions: str


# ------------------------
# Supervisor
# ------------------------

class Workflow(TypedDict):
    current_goal: str
    next_agent: str | None
    completed_steps: list[str]


# ------------------------
# Master State
# ------------------------

class HospitalState(TypedDict):
    patient: Patient
    admission: Admission
    insurance: Insurance
    doctor: Doctor
    lab: Lab
    pharmacy: Pharmacy
    billing: Billing
    discharge: Discharge
    workflow: Workflow
    messages: Annotated[list, add_messages]
    error: str | None