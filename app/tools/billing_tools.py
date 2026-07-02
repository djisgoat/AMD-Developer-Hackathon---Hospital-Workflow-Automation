"""Billing tools for cost calculation and payment processing."""

import random
from datetime import datetime

from langchain_core.tools import tool


# Realistic Indian hospital pricing (in INR)
SERVICE_PRICING = {
    "consultation": {
        "general": 500.0,
        "specialist": 1000.0,
        "super_specialist": 2000.0,
    },
    "lab_tests": {
        "CBC": 450.0,
        "Blood Sugar": 250.0,
        "Lipid Panel": 800.0,
        "Liver Function Test": 900.0,
        "Kidney Function Test": 850.0,
        "Thyroid Profile": 700.0,
        "Urinalysis": 350.0,
        "X-Ray": 600.0,
        "CT Scan": 5000.0,
        "MRI": 8000.0,
        "ECG": 400.0,
        "Echo": 2500.0,
        "Ultrasound": 1500.0,
    },
    "room_charges": {
        "General": 1500.0,      # per day
        "Semi-Private": 3500.0,  # per day
        "Private": 6000.0,      # per day
        "ICU": 15000.0,         # per day
        "Deluxe": 10000.0,      # per day
    },
    "medicines": {
        "basic": 200.0,
        "standard": 500.0,
        "premium": 1500.0,
    },
    "procedures": {
        "minor": 5000.0,
        "major": 50000.0,
        "surgery_minor": 25000.0,
        "surgery_major": 150000.0,
    },
}

# GST rate for healthcare services
GST_RATE = 0.05  # 5% GST on hospital room charges above ₹5000/day


@tool
def calculate_costs(services: dict) -> dict:
    """Calculate itemized hospital costs for provided services.

    Computes a detailed cost breakdown for all services rendered during a
    hospital stay, including consultation, lab tests, medicines, room charges,
    and procedures. Applies applicable GST and returns the grand total.

    Uses realistic Indian hospital pricing.

    Args:
        services: Dictionary of services rendered. Supported keys:
            - consultation (str): Type of consultation ('general', 'specialist',
              'super_specialist').
            - lab_tests (list[str]): List of lab test names
              (e.g., ['CBC', 'Blood Sugar']).
            - medicines (list[str] or str): Medicine tier ('basic', 'standard',
              'premium') or list of medicine names.
            - room_charges (dict): Room details with 'type' (str) and 'days' (int).
            - procedures (list[str]): List of procedure types
              (e.g., ['minor', 'surgery_major']).

    Returns:
        A dict with keys:
            - itemized_costs (dict): Breakdown of costs by category.
            - total_cost (float): Sum of all costs before tax.
            - tax (float): Applicable GST amount.
            - grand_total (float): Total cost including tax.
    """
    itemized_costs = {}
    total_cost = 0.0

    # Consultation charges
    if "consultation" in services:
        consult_type = services["consultation"]
        if isinstance(consult_type, str):
            cost = SERVICE_PRICING["consultation"].get(consult_type, 500.0)
        else:
            cost = 500.0
        itemized_costs["consultation"] = cost
        total_cost += cost

    # Lab test charges
    if "lab_tests" in services:
        lab_tests = services["lab_tests"]
        if isinstance(lab_tests, list):
            lab_total = 0.0
            lab_breakdown = {}
            for test in lab_tests:
                test_cost = SERVICE_PRICING["lab_tests"].get(test, 500.0)
                lab_breakdown[test] = test_cost
                lab_total += test_cost
            itemized_costs["lab_tests"] = lab_breakdown
            itemized_costs["lab_tests_total"] = lab_total
            total_cost += lab_total

    # Medicine charges
    if "medicines" in services:
        medicines = services["medicines"]
        if isinstance(medicines, str):
            med_cost = SERVICE_PRICING["medicines"].get(medicines, 500.0)
            itemized_costs["medicines"] = med_cost
            total_cost += med_cost
        elif isinstance(medicines, list):
            # Estimate ₹150-500 per medicine
            med_total = sum(random.uniform(150.0, 500.0) for _ in medicines)
            med_total = round(med_total, 2)
            itemized_costs["medicines"] = med_total
            total_cost += med_total

    # Room charges
    if "room_charges" in services:
        room_info = services["room_charges"]
        if isinstance(room_info, dict):
            room_type = room_info.get("type", "General")
            days = room_info.get("days", 1)
            daily_rate = SERVICE_PRICING["room_charges"].get(room_type, 1500.0)
            room_total = daily_rate * days
            itemized_costs["room_charges"] = {
                "type": room_type,
                "daily_rate": daily_rate,
                "days": days,
                "total": room_total,
            }
            total_cost += room_total

    # Procedure charges
    if "procedures" in services:
        procedures = services["procedures"]
        if isinstance(procedures, list):
            proc_total = 0.0
            proc_breakdown = {}
            for proc in procedures:
                proc_cost = SERVICE_PRICING["procedures"].get(proc, 5000.0)
                proc_breakdown[proc] = proc_cost
                proc_total += proc_cost
            itemized_costs["procedures"] = proc_breakdown
            itemized_costs["procedures_total"] = proc_total
            total_cost += proc_total

    # Calculate GST (5% on room charges > ₹5000/day)
    tax = 0.0
    if "room_charges" in itemized_costs:
        room_data = itemized_costs["room_charges"]
        if isinstance(room_data, dict) and room_data.get("daily_rate", 0) > 5000:
            tax = room_data["total"] * GST_RATE

    total_cost = round(total_cost, 2)
    tax = round(tax, 2)
    grand_total = round(total_cost + tax, 2)

    return {
        "itemized_costs": itemized_costs,
        "total_cost": total_cost,
        "tax": tax,
        "grand_total": grand_total,
    }


@tool
def process_payment(amount: float, method: str) -> dict:
    """Process a payment transaction for hospital services.

    Records the payment with a unique transaction ID, validates the payment
    method, and returns a confirmation receipt. Supported payment methods
    include Cash, Credit Card, Debit Card, UPI, Net Banking, and Insurance.

    Args:
        amount: Total payment amount in INR (e.g., 15750.50).
        method: Payment method. Accepted values: 'Cash', 'Credit Card',
            'Debit Card', 'UPI', 'Net Banking', 'Insurance'.

    Returns:
        A dict with keys:
            - transaction_id (str): Unique transaction identifier.
            - amount_paid (float): Amount that was processed.
            - method (str): Payment method used.
            - status (str): Payment status ('Success' or 'Failed').
            - timestamp (str): Payment timestamp.
    """
    valid_methods = ["cash", "credit card", "debit card", "upi", "net banking", "insurance"]

    method_lower = method.lower().strip()

    # Simulate payment success (95% success rate)
    is_success = random.random() < 0.95

    transaction_id = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100000, 999999)}"

    if method_lower not in valid_methods:
        return {
            "transaction_id": transaction_id,
            "amount_paid": 0.0,
            "method": method,
            "status": f"Failed - Invalid payment method '{method}'. "
                      f"Accepted methods: {', '.join(valid_methods)}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    if is_success:
        return {
            "transaction_id": transaction_id,
            "amount_paid": round(amount, 2),
            "method": method,
            "status": "Success",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    else:
        return {
            "transaction_id": transaction_id,
            "amount_paid": 0.0,
            "method": method,
            "status": "Failed - Payment declined. Please retry or use a different method.",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
