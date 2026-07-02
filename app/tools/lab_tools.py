"""Lab tools for ordering tests and fetching results."""

import random
from datetime import datetime, timedelta

from langchain_core.tools import tool


# Simulated reference data for common lab tests
LAB_TEST_REFERENCES = {
    "CBC": {
        "full_name": "Complete Blood Count",
        "components": [
            {"test_name": "Hemoglobin", "unit": "g/dL", "reference_range": "12.0 - 17.5", "min_val": 8.0, "max_val": 19.0},
            {"test_name": "WBC Count", "unit": "cells/mcL", "reference_range": "4,500 - 11,000", "min_val": 3000, "max_val": 15000},
            {"test_name": "Platelet Count", "unit": "cells/mcL", "reference_range": "150,000 - 400,000", "min_val": 100000, "max_val": 500000},
            {"test_name": "RBC Count", "unit": "million/mcL", "reference_range": "4.5 - 5.5", "min_val": 3.5, "max_val": 6.5},
        ],
    },
    "Blood Sugar": {
        "full_name": "Blood Glucose Test",
        "components": [
            {"test_name": "Fasting Blood Sugar", "unit": "mg/dL", "reference_range": "70 - 100", "min_val": 55, "max_val": 250},
            {"test_name": "Post-Prandial Blood Sugar", "unit": "mg/dL", "reference_range": "< 140", "min_val": 80, "max_val": 300},
            {"test_name": "HbA1c", "unit": "%", "reference_range": "4.0 - 5.6", "min_val": 3.5, "max_val": 12.0},
        ],
    },
    "Lipid Panel": {
        "full_name": "Lipid Profile",
        "components": [
            {"test_name": "Total Cholesterol", "unit": "mg/dL", "reference_range": "< 200", "min_val": 120, "max_val": 320},
            {"test_name": "LDL Cholesterol", "unit": "mg/dL", "reference_range": "< 100", "min_val": 50, "max_val": 220},
            {"test_name": "HDL Cholesterol", "unit": "mg/dL", "reference_range": "> 40", "min_val": 25, "max_val": 90},
            {"test_name": "Triglycerides", "unit": "mg/dL", "reference_range": "< 150", "min_val": 60, "max_val": 400},
        ],
    },
    "Liver Function Test": {
        "full_name": "Liver Function Test (LFT)",
        "components": [
            {"test_name": "SGPT (ALT)", "unit": "U/L", "reference_range": "7 - 56", "min_val": 5, "max_val": 120},
            {"test_name": "SGOT (AST)", "unit": "U/L", "reference_range": "10 - 40", "min_val": 8, "max_val": 100},
            {"test_name": "Bilirubin (Total)", "unit": "mg/dL", "reference_range": "0.1 - 1.2", "min_val": 0.1, "max_val": 5.0},
            {"test_name": "Albumin", "unit": "g/dL", "reference_range": "3.5 - 5.5", "min_val": 2.0, "max_val": 6.0},
        ],
    },
    "Kidney Function Test": {
        "full_name": "Renal Function Test (KFT)",
        "components": [
            {"test_name": "Creatinine", "unit": "mg/dL", "reference_range": "0.7 - 1.3", "min_val": 0.4, "max_val": 4.0},
            {"test_name": "Blood Urea Nitrogen (BUN)", "unit": "mg/dL", "reference_range": "7 - 20", "min_val": 5, "max_val": 50},
            {"test_name": "Uric Acid", "unit": "mg/dL", "reference_range": "3.4 - 7.0", "min_val": 2.0, "max_val": 12.0},
        ],
    },
    "Thyroid Profile": {
        "full_name": "Thyroid Function Test",
        "components": [
            {"test_name": "TSH", "unit": "mIU/L", "reference_range": "0.4 - 4.0", "min_val": 0.1, "max_val": 15.0},
            {"test_name": "T3", "unit": "ng/dL", "reference_range": "80 - 200", "min_val": 40, "max_val": 300},
            {"test_name": "T4", "unit": "mcg/dL", "reference_range": "5.1 - 14.1", "min_val": 2.0, "max_val": 20.0},
        ],
    },
    "Urinalysis": {
        "full_name": "Urine Routine & Microscopy",
        "components": [
            {"test_name": "pH", "unit": "", "reference_range": "4.5 - 8.0", "min_val": 4.0, "max_val": 9.0},
            {"test_name": "Specific Gravity", "unit": "", "reference_range": "1.005 - 1.030", "min_val": 1.001, "max_val": 1.040},
            {"test_name": "Protein", "unit": "mg/dL", "reference_range": "< 15", "min_val": 0, "max_val": 100},
        ],
    },
}


def _generate_result_for_component(component: dict) -> dict:
    """Generate a simulated result for a single test component."""
    value = round(random.uniform(component["min_val"], component["max_val"]), 2)

    # Format large numbers with commas
    if value > 1000:
        value_str = f"{int(value):,}"
    else:
        value_str = str(value)

    # Determine status based on reference range
    ref = component["reference_range"]
    if "-" in ref:
        parts = ref.replace(",", "").split("-")
        try:
            low = float(parts[0].strip())
            high = float(parts[1].strip())
            raw_value = float(str(value).replace(",", ""))
            if raw_value < low:
                status = "Low"
            elif raw_value > high:
                status = "High"
            else:
                status = "Normal"
        except ValueError:
            status = "Normal"
    elif ref.startswith("<"):
        threshold = float(ref.replace("<", "").replace(",", "").strip())
        status = "Normal" if value < threshold else "High"
    elif ref.startswith(">"):
        threshold = float(ref.replace(">", "").replace(",", "").strip())
        status = "Normal" if value > threshold else "Low"
    else:
        status = "Normal"

    return {
        "test_name": component["test_name"],
        "value": value_str,
        "unit": component["unit"],
        "reference_range": component["reference_range"],
        "status": status,
    }


@tool
def order_tests(test_names: list[str], patient_id: str) -> dict:
    """Order laboratory tests for a patient.

    Creates a lab test order with a unique order ID and estimated completion
    time. The ordered tests are queued for processing in the hospital
    laboratory system.

    Args:
        test_names: List of test names to order (e.g., ['CBC', 'Blood Sugar',
            'Lipid Panel', 'Liver Function Test']).
        patient_id: The patient's unique ID (e.g., 'PID-20260702-4521').

    Returns:
        A dict with keys:
            - order_id (str): Unique lab order identifier.
            - tests_ordered (list[str]): Confirmed list of tests ordered.
            - estimated_completion (str): Estimated result availability time
              in 'YYYY-MM-DD HH:MM' format.
            - status (str): Current order status.
    """
    order_id = f"LAB-{datetime.now().strftime('%Y%m%d')}-{random.randint(10000, 99999)}"

    # Estimate completion: 2-6 hours from now
    hours_to_complete = random.randint(2, 6)
    estimated_completion = (datetime.now() + timedelta(hours=hours_to_complete)).strftime("%Y-%m-%d %H:%M")

    return {
        "order_id": order_id,
        "tests_ordered": test_names,
        "estimated_completion": estimated_completion,
        "status": "Order Placed - Samples to be collected",
    }


@tool
def fetch_lab_results(order_id: str, test_names: list[str]) -> dict:
    """Fetch laboratory test results for a completed order.

    Retrieves simulated but realistic lab results for the specified tests.
    Each test may return multiple component values with reference ranges
    and status indicators (Normal, High, Low).

    Args:
        order_id: The lab order ID to fetch results for
            (e.g., 'LAB-20260702-54321').
        test_names: List of test names to retrieve results for
            (e.g., ['CBC', 'Blood Sugar']).

    Returns:
        A dict with keys:
            - order_id (str): The lab order identifier.
            - results (list[dict]): List of result dicts, each containing:
                - test_name (str): Name of the test component.
                - value (str): Measured value.
                - unit (str): Unit of measurement.
                - reference_range (str): Normal reference range.
                - status (str): 'Normal', 'High', or 'Low'.
            - generated_at (str): Timestamp of result generation.
    """
    results = []

    for test_name in test_names:
        # Normalize test name for lookup
        test_key = None
        for key in LAB_TEST_REFERENCES:
            if key.lower() in test_name.lower() or test_name.lower() in key.lower():
                test_key = key
                break

        if test_key:
            test_data = LAB_TEST_REFERENCES[test_key]
            for component in test_data["components"]:
                results.append(_generate_result_for_component(component))
        else:
            # Generic result for unknown tests
            results.append({
                "test_name": test_name,
                "value": str(round(random.uniform(1.0, 100.0), 2)),
                "unit": "units",
                "reference_range": "Varies",
                "status": random.choice(["Normal", "Normal", "Normal", "High", "Low"]),
            })

    return {
        "order_id": order_id,
        "results": results,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
