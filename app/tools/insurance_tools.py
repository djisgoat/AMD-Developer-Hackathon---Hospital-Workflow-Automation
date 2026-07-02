"""Insurance tools for policy verification and coverage checks."""

import random
from datetime import datetime, timedelta

from langchain_core.tools import tool


@tool
def verify_insurance(policy_number: str, provider: str) -> dict:
    """Verify a patient's insurance policy validity with the provider.

    Checks whether the given insurance policy is active and valid. Policies
    with numbers starting with 'POL' are treated as valid; all others are
    rejected. Returns policy holder information and expiry details.

    Args:
        policy_number: The insurance policy number to verify
            (e.g., 'POL-2024-78432').
        provider: Name of the insurance provider
            (e.g., 'Star Health', 'ICICI Lombard').

    Returns:
        A dict with keys:
            - is_valid (bool): Whether the policy is currently active.
            - policy_holder (str): Name associated with the policy.
            - expiry_date (str): Policy expiration date in YYYY-MM-DD format.
            - status (str): Human-readable status message.
    """
    is_valid = policy_number.upper().startswith("POL")

    if is_valid:
        expiry_date = (datetime.now() + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d")
        return {
            "is_valid": True,
            "policy_holder": f"Policyholder of {policy_number}",
            "expiry_date": expiry_date,
            "status": f"Active policy with {provider}. Verified successfully.",
        }
    else:
        return {
            "is_valid": False,
            "policy_holder": "N/A",
            "expiry_date": "N/A",
            "status": f"Policy {policy_number} not found or invalid with {provider}. "
                       "Please check the policy number and try again.",
        }


@tool
def check_coverage(policy_number: str, treatment_type: str) -> dict:
    """Check insurance coverage details for a specific treatment type.

    Returns coverage percentage, maximum coverage amount, copay percentage,
    and any remarks based on the treatment type. Different treatments have
    varying coverage levels.

    Args:
        policy_number: The insurance policy number (e.g., 'POL-2024-78432').
        treatment_type: Type of treatment to check coverage for. Common types
            include 'surgery', 'consultation', 'diagnostic', 'emergency',
            'maternity', 'dental'.

    Returns:
        A dict with keys:
            - coverage_percentage (float): Percentage of costs covered.
            - max_coverage_amount (float): Maximum amount covered in INR.
            - copay_percentage (float): Patient's copay percentage.
            - remarks (str): Additional coverage notes or restrictions.
    """
    treatment_type_lower = treatment_type.lower().strip()

    coverage_map = {
        "surgery": {
            "coverage_percentage": 80.0,
            "max_coverage_amount": 500000.0,
            "copay_percentage": 20.0,
            "remarks": "Pre-authorization required for elective surgeries. "
                       "Emergency surgeries covered without prior approval.",
        },
        "consultation": {
            "coverage_percentage": 100.0,
            "max_coverage_amount": 5000.0,
            "copay_percentage": 0.0,
            "remarks": "Covers up to 2 specialist consultations per visit. "
                       "Follow-up consultations within 7 days are free.",
        },
        "diagnostic": {
            "coverage_percentage": 90.0,
            "max_coverage_amount": 50000.0,
            "copay_percentage": 10.0,
            "remarks": "Covers blood tests, imaging (X-ray, CT, MRI), and "
                       "pathology. Advanced genetic testing may require approval.",
        },
        "emergency": {
            "coverage_percentage": 100.0,
            "max_coverage_amount": 750000.0,
            "copay_percentage": 0.0,
            "remarks": "Full coverage for emergency room visits, ambulance, and "
                       "stabilization procedures. No pre-authorization needed.",
        },
        "maternity": {
            "coverage_percentage": 70.0,
            "max_coverage_amount": 200000.0,
            "copay_percentage": 30.0,
            "remarks": "Covers normal and cesarean delivery. 9-month waiting "
                       "period applies for new policies.",
        },
        "dental": {
            "coverage_percentage": 50.0,
            "max_coverage_amount": 25000.0,
            "copay_percentage": 50.0,
            "remarks": "Covers basic dental procedures. Cosmetic dentistry is "
                       "not covered under this plan.",
        },
        "physiotherapy": {
            "coverage_percentage": 75.0,
            "max_coverage_amount": 30000.0,
            "copay_percentage": 25.0,
            "remarks": "Covers up to 20 sessions per policy year. "
                       "Requires doctor's referral.",
        },
    }

    if treatment_type_lower in coverage_map:
        return coverage_map[treatment_type_lower]
    else:
        # Default coverage for unlisted treatments
        return {
            "coverage_percentage": 60.0,
            "max_coverage_amount": 100000.0,
            "copay_percentage": 40.0,
            "remarks": f"Standard coverage applied for '{treatment_type}'. "
                       "Contact insurer for specific policy terms and conditions.",
        }
