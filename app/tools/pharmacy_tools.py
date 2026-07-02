"""Pharmacy tools for drug interaction checks and medication dispensing."""

import random
from datetime import datetime

from langchain_core.tools import tool


# Common drug-allergy interaction mapping
KNOWN_INTERACTIONS = {
    "aspirin": ["nsaid", "blood thinner", "anticoagulant"],
    "ibuprofen": ["nsaid", "aspirin", "blood thinner"],
    "amoxicillin": ["penicillin", "cephalosporin"],
    "penicillin": ["amoxicillin", "cephalosporin"],
    "cephalosporin": ["penicillin", "amoxicillin"],
    "sulfonamide": ["sulfa"],
    "metformin": ["contrast dye"],
    "warfarin": ["aspirin", "ibuprofen", "nsaid"],
    "lisinopril": ["ace inhibitor", "potassium"],
    "atorvastatin": ["grapefruit", "fibrate"],
    "omeprazole": ["clopidogrel"],
    "clopidogrel": ["omeprazole", "ppi"],
    "metoprolol": ["beta blocker", "calcium channel blocker"],
    "ciprofloxacin": ["fluoroquinolone", "theophylline"],
}

# Standard dosage information for common medications
MEDICATION_DOSAGE = {
    "paracetamol": {"dosage": "500mg", "frequency": "Every 6 hours", "duration": "5 days"},
    "amoxicillin": {"dosage": "500mg", "frequency": "Every 8 hours", "duration": "7 days"},
    "ibuprofen": {"dosage": "400mg", "frequency": "Every 8 hours", "duration": "5 days"},
    "omeprazole": {"dosage": "20mg", "frequency": "Once daily (before breakfast)", "duration": "14 days"},
    "metformin": {"dosage": "500mg", "frequency": "Twice daily (with meals)", "duration": "Ongoing"},
    "atorvastatin": {"dosage": "10mg", "frequency": "Once daily (at bedtime)", "duration": "Ongoing"},
    "aspirin": {"dosage": "75mg", "frequency": "Once daily", "duration": "Ongoing"},
    "azithromycin": {"dosage": "500mg", "frequency": "Once daily", "duration": "3 days"},
    "ciprofloxacin": {"dosage": "500mg", "frequency": "Twice daily", "duration": "7 days"},
    "metoprolol": {"dosage": "50mg", "frequency": "Twice daily", "duration": "Ongoing"},
    "lisinopril": {"dosage": "10mg", "frequency": "Once daily", "duration": "Ongoing"},
    "warfarin": {"dosage": "5mg", "frequency": "Once daily", "duration": "As directed"},
    "clopidogrel": {"dosage": "75mg", "frequency": "Once daily", "duration": "Ongoing"},
    "prednisolone": {"dosage": "10mg", "frequency": "Once daily (morning)", "duration": "5 days (tapering)"},
    "cetirizine": {"dosage": "10mg", "frequency": "Once daily", "duration": "7 days"},
    "pantoprazole": {"dosage": "40mg", "frequency": "Once daily (before breakfast)", "duration": "14 days"},
}


@tool
def check_drug_interactions(medicines: list[str], allergies: list[str]) -> dict:
    """Check for potential drug interactions and allergy conflicts.

    Analyzes the prescribed medicines against the patient's known allergies
    and checks for known drug-drug and drug-allergy interactions. This is
    a critical safety check before dispensing medications.

    Args:
        medicines: List of medicine names to check
            (e.g., ['Amoxicillin', 'Ibuprofen', 'Omeprazole']).
        allergies: List of known patient allergies
            (e.g., ['Penicillin', 'Sulfa']).

    Returns:
        A dict with keys:
            - interactions_found (bool): Whether any interactions were detected.
            - details (list[str]): List of interaction/allergy warnings.
            - safe_to_proceed (bool): Whether it is safe to dispense all medicines.
    """
    details = []
    interactions_found = False

    medicines_lower = [m.lower().strip() for m in medicines]
    allergies_lower = [a.lower().strip() for a in allergies]

    # Check each medicine against allergies
    for medicine in medicines_lower:
        # Direct allergy match
        for allergy in allergies_lower:
            if allergy in medicine or medicine in allergy:
                details.append(
                    f"⚠️ ALLERGY ALERT: '{medicine.title()}' matches known allergy "
                    f"'{allergy.title()}'. Do NOT administer."
                )
                interactions_found = True

        # Check known cross-reactivity
        if medicine in KNOWN_INTERACTIONS:
            for allergy in allergies_lower:
                if allergy in KNOWN_INTERACTIONS[medicine]:
                    details.append(
                        f"⚠️ CROSS-REACTIVITY: '{medicine.title()}' may cross-react "
                        f"with allergy to '{allergy.title()}'. Consult physician."
                    )
                    interactions_found = True

    # Check drug-drug interactions
    for i, med1 in enumerate(medicines_lower):
        for med2 in medicines_lower[i + 1:]:
            if med1 in KNOWN_INTERACTIONS and med2 in KNOWN_INTERACTIONS.get(med1, []):
                details.append(
                    f"⚠️ DRUG INTERACTION: '{med1.title()}' and '{med2.title()}' "
                    f"have a known interaction. Review dosage or consider alternatives."
                )
                interactions_found = True
            elif med2 in KNOWN_INTERACTIONS and med1 in KNOWN_INTERACTIONS.get(med2, []):
                details.append(
                    f"⚠️ DRUG INTERACTION: '{med2.title()}' and '{med1.title()}' "
                    f"have a known interaction. Review dosage or consider alternatives."
                )
                interactions_found = True

    if not interactions_found:
        details.append("✅ No interactions or allergy conflicts detected. Safe to proceed.")

    return {
        "interactions_found": interactions_found,
        "details": details,
        "safe_to_proceed": not interactions_found,
    }


@tool
def dispense_medication(medicines: list[str], patient_id: str) -> dict:
    """Dispense prescribed medications to a patient from the hospital pharmacy.

    Prepares and records the dispensing of medications with appropriate dosage,
    frequency, and duration information. Generates a unique dispensing ID for
    tracking purposes.

    Args:
        medicines: List of medicine names to dispense
            (e.g., ['Paracetamol', 'Amoxicillin', 'Omeprazole']).
        patient_id: The patient's unique ID (e.g., 'PID-20260702-4521').

    Returns:
        A dict with keys:
            - dispensed (list[dict]): List of dispensed items, each containing:
                - name (str): Medicine name.
                - dosage (str): Prescribed dosage.
                - frequency (str): Administration frequency.
                - duration (str): Duration of the course.
            - dispensing_id (str): Unique dispensing transaction ID.
            - timestamp (str): Dispensing timestamp.
    """
    dispensed_items = []

    for medicine in medicines:
        med_lower = medicine.lower().strip()

        if med_lower in MEDICATION_DOSAGE:
            dosage_info = MEDICATION_DOSAGE[med_lower]
            dispensed_items.append({
                "name": medicine.title(),
                "dosage": dosage_info["dosage"],
                "frequency": dosage_info["frequency"],
                "duration": dosage_info["duration"],
            })
        else:
            # Default dosage for unknown medications
            dispensed_items.append({
                "name": medicine.title(),
                "dosage": "As prescribed",
                "frequency": "As directed by physician",
                "duration": "As directed",
            })

    dispensing_id = f"DISP-{datetime.now().strftime('%Y%m%d')}-{random.randint(10000, 99999)}"

    return {
        "dispensed": dispensed_items,
        "dispensing_id": dispensing_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
