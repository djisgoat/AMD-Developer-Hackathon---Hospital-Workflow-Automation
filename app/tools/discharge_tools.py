"""Discharge tools for generating discharge summaries."""

import random
from datetime import datetime

from langchain_core.tools import tool


@tool
def generate_discharge_summary(
    patient_name: str,
    diagnosis: str,
    treatment: str,
    follow_up_date: str,
) -> dict:
    """Generate a comprehensive discharge summary document for a patient.

    Creates a formatted discharge summary that includes patient details,
    diagnosis, treatment received, discharge instructions, and follow-up
    information. This document is provided to the patient upon discharge.

    Args:
        patient_name: Full name of the patient being discharged.
        diagnosis: Primary diagnosis or condition treated during the stay
            (e.g., 'Acute Myocardial Infarction').
        treatment: Description of treatment provided during hospitalization
            (e.g., 'Angioplasty with stent placement, dual antiplatelet therapy').
        follow_up_date: Recommended follow-up appointment date in YYYY-MM-DD
            format (e.g., '2026-07-15').

    Returns:
        A dict with keys:
            - summary_id (str): Unique discharge summary identifier.
            - document (str): Formatted multi-line discharge summary text.
            - generated_at (str): Timestamp when the summary was generated.
    """
    summary_id = f"DS-{datetime.now().strftime('%Y%m%d')}-{random.randint(10000, 99999)}"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    document = f"""
{'='*65}
              HOSPITAL DISCHARGE SUMMARY
{'='*65}

Summary ID    : {summary_id}
Date          : {generated_at}

{'─'*65}
PATIENT INFORMATION
{'─'*65}
Patient Name  : {patient_name}
Discharge Date: {datetime.now().strftime('%Y-%m-%d')}

{'─'*65}
CLINICAL DETAILS
{'─'*65}
Primary Diagnosis:
  {diagnosis}

Treatment Provided:
  {treatment}

{'─'*65}
DISCHARGE INSTRUCTIONS
{'─'*65}
1. Take all prescribed medications as directed.
2. Follow the recommended diet plan provided by the dietician.
3. Avoid strenuous physical activity for the advised duration.
4. Watch for warning signs: fever > 101°F, severe pain, unusual
   swelling, or any sudden changes in condition.
5. Keep all wounds clean and dry. Change dressings as instructed.
6. Stay well hydrated and get adequate rest.

{'─'*65}
FOLLOW-UP
{'─'*65}
Next Appointment : {follow_up_date}
Note             : Please bring this discharge summary and all
                   prescribed medication to your follow-up visit.

{'─'*65}
EMERGENCY CONTACT
{'─'*65}
In case of emergency, contact the hospital helpline:
  📞 +91-1800-XXX-XXXX (24/7)
  🏥 Emergency Department - Ground Floor

{'='*65}
This is a computer-generated document. No signature required.
{'='*65}
""".strip()

    return {
        "summary_id": summary_id,
        "document": document,
        "generated_at": generated_at,
    }
