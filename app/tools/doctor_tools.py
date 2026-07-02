"""Doctor tools for looking up physician availability."""

import random
from datetime import datetime, timedelta

from langchain_core.tools import tool


# Hardcoded roster of doctors per department
DOCTOR_ROSTER = {
    "Cardiology": [
        {"doctor_name": "Dr. Anil Kapoor", "doctor_id": "DOC-CARD-001", "specialization": "Interventional Cardiology"},
        {"doctor_name": "Dr. Meena Sharma", "doctor_id": "DOC-CARD-002", "specialization": "Electrophysiology"},
        {"doctor_name": "Dr. Rajesh Verma", "doctor_id": "DOC-CARD-003", "specialization": "Pediatric Cardiology"},
    ],
    "Neurology": [
        {"doctor_name": "Dr. Priya Nair", "doctor_id": "DOC-NEUR-001", "specialization": "Stroke & Cerebrovascular"},
        {"doctor_name": "Dr. Suresh Iyer", "doctor_id": "DOC-NEUR-002", "specialization": "Epilepsy & Seizure Disorders"},
    ],
    "Orthopedics": [
        {"doctor_name": "Dr. Vikram Singh", "doctor_id": "DOC-ORTH-001", "specialization": "Joint Replacement Surgery"},
        {"doctor_name": "Dr. Anjali Desai", "doctor_id": "DOC-ORTH-002", "specialization": "Sports Medicine"},
        {"doctor_name": "Dr. Ramesh Gupta", "doctor_id": "DOC-ORTH-003", "specialization": "Spine Surgery"},
    ],
    "General Medicine": [
        {"doctor_name": "Dr. Kavita Reddy", "doctor_id": "DOC-GENM-001", "specialization": "Internal Medicine"},
        {"doctor_name": "Dr. Arjun Patel", "doctor_id": "DOC-GENM-002", "specialization": "Family Medicine"},
    ],
    "Pulmonology": [
        {"doctor_name": "Dr. Sunita Rao", "doctor_id": "DOC-PULM-001", "specialization": "Respiratory Medicine"},
        {"doctor_name": "Dr. Manish Tiwari", "doctor_id": "DOC-PULM-002", "specialization": "Critical Care Pulmonology"},
    ],
    "Gastroenterology": [
        {"doctor_name": "Dr. Deepak Joshi", "doctor_id": "DOC-GAST-001", "specialization": "Hepatology"},
        {"doctor_name": "Dr. Neha Kulkarni", "doctor_id": "DOC-GAST-002", "specialization": "Endoscopy & GI Surgery"},
    ],
    "Dermatology": [
        {"doctor_name": "Dr. Pooja Mehta", "doctor_id": "DOC-DERM-001", "specialization": "Clinical Dermatology"},
    ],
    "Emergency Medicine": [
        {"doctor_name": "Dr. Sanjay Kumar", "doctor_id": "DOC-EMER-001", "specialization": "Trauma & Emergency Care"},
        {"doctor_name": "Dr. Ritu Saxena", "doctor_id": "DOC-EMER-002", "specialization": "Acute Care Medicine"},
    ],
}


@tool
def lookup_doctor_availability(department: str) -> dict:
    """Look up available doctors in a specific hospital department.

    Searches the doctor roster for the given department and returns the
    details of an available doctor, including their next available
    appointment slot. If no doctors are found for the department, a
    default General Medicine doctor is returned.

    Args:
        department: Name of the hospital department to search
            (e.g., 'Cardiology', 'Neurology', 'Orthopedics').

    Returns:
        A dict with keys:
            - doctor_name (str): Full name of the doctor.
            - doctor_id (str): Unique doctor identifier.
            - specialization (str): Doctor's area of specialization.
            - available (bool): Whether the doctor is currently available.
            - next_available_slot (str): Next available appointment in
              'YYYY-MM-DD HH:MM' format.
    """
    doctors = DOCTOR_ROSTER.get(department, DOCTOR_ROSTER["General Medicine"])
    doctor = random.choice(doctors)

    # Simulate availability (80% chance of being available)
    available = random.random() < 0.8

    if available:
        # Available within the next few hours
        slot_offset = timedelta(minutes=random.randint(15, 120))
    else:
        # Next available slot is tomorrow or later
        slot_offset = timedelta(hours=random.randint(12, 48))

    next_slot = (datetime.now() + slot_offset).strftime("%Y-%m-%d %H:%M")

    return {
        "doctor_name": doctor["doctor_name"],
        "doctor_id": doctor["doctor_id"],
        "specialization": doctor["specialization"],
        "available": available,
        "next_available_slot": next_slot,
    }
