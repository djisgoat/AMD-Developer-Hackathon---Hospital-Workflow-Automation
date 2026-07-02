"""Admission tools for patient registration and department assignment."""

import random
from datetime import datetime

from langchain_core.tools import tool


@tool
def generate_patient_id(name: str) -> str:
    """Generate a unique patient ID for a new hospital admission.

    Creates a patient identifier in the format 'PID-YYYYMMDD-XXXX' using the
    current date and a random 4-digit number. This ID is used to track the
    patient throughout their hospital stay.

    Args:
        name: Full name of the patient being admitted.

    Returns:
        A unique patient ID string in the format 'PID-YYYYMMDD-XXXX'.
    """
    date_str = datetime.now().strftime("%Y%m%d")
    random_suffix = f"{random.randint(1000, 9999)}"
    patient_id = f"PID-{date_str}-{random_suffix}"
    return patient_id


@tool
def assign_department(symptoms: list[str], priority: str) -> dict:
    """Assign a hospital department, ward type, and bed number based on patient symptoms and priority.

    Analyzes the reported symptoms to determine the most appropriate department
    and uses the priority level to decide the ward type (ICU, Semi-Private, or
    General). A bed number is randomly assigned within the selected ward.

    Args:
        symptoms: List of symptom descriptions reported by the patient
            (e.g., ['chest pain', 'shortness of breath']).
        priority: Triage priority level. Must be one of:
            'Critical', 'High', 'Medium', or 'Low'.

    Returns:
        A dict with keys:
            - department (str): Assigned hospital department.
            - ward_type (str): Type of ward based on priority.
            - bed_number (str): Assigned bed identifier.
    """
    # Symptom keyword to department mapping
    symptom_department_map = {
        "chest pain": "Cardiology",
        "heart": "Cardiology",
        "palpitation": "Cardiology",
        "shortness of breath": "Pulmonology",
        "breathing": "Pulmonology",
        "cough": "Pulmonology",
        "headache": "Neurology",
        "seizure": "Neurology",
        "dizziness": "Neurology",
        "numbness": "Neurology",
        "fracture": "Orthopedics",
        "bone pain": "Orthopedics",
        "joint pain": "Orthopedics",
        "sprain": "Orthopedics",
        "abdominal pain": "Gastroenterology",
        "nausea": "Gastroenterology",
        "vomiting": "Gastroenterology",
        "diarrhea": "Gastroenterology",
        "fever": "General Medicine",
        "rash": "Dermatology",
        "skin": "Dermatology",
        "burn": "Emergency Medicine",
        "trauma": "Emergency Medicine",
        "bleeding": "Emergency Medicine",
    }

    # Determine department from symptoms
    department = "General Medicine"
    symptoms_lower = [s.lower().strip() for s in symptoms]

    for symptom in symptoms_lower:
        for keyword, dept in symptom_department_map.items():
            if keyword in symptom:
                department = dept
                break
        if department != "General Medicine":
            break

    # Ward type based on priority
    priority_ward_map = {
        "Critical": "ICU",
        "High": "ICU",
        "Medium": "Semi-Private",
        "Low": "General",
    }
    ward_type = priority_ward_map.get(priority, "General")

    # Generate bed number
    ward_prefix_map = {
        "ICU": "ICU",
        "Semi-Private": "SP",
        "General": "GEN",
    }
    prefix = ward_prefix_map.get(ward_type, "GEN")
    bed_number = f"{prefix}-{random.randint(100, 999)}"

    return {
        "department": department,
        "ward_type": ward_type,
        "bed_number": bed_number,
    }
