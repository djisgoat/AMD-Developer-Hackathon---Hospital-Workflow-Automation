"""LangGraph workflow — hub-and-spoke topology.

Defines the ``StateGraph`` that orchestrates the hospital workflow.
The Supervisor is the hub; every specialist agent is a spoke.
All agents return control to the supervisor after completing their work.
The supervisor uses ``Command(goto=...)`` to dynamically route.
"""

from langgraph.graph import StateGraph, START, END

from app.state.hospital_state import HospitalState

# Import all agent classes
from app.agents.supervisor import SupervisorAgent
from app.agents.admission import AdmissionAgent
from app.agents.insurance import InsuranceAgent
from app.agents.doctor import DoctorAgent
from app.agents.lab import LabAgent
from app.agents.pharmacy import PharmacyAgent
from app.agents.billing import BillingAgent
from app.agents.discharge import DischargeAgent


# ------------------------------------------------------------------
# Instantiate agents (singletons — one per workflow)
# ------------------------------------------------------------------

_supervisor = SupervisorAgent()
_admission = AdmissionAgent()
_insurance = InsuranceAgent()
_doctor = DoctorAgent()
_lab = LabAgent()
_pharmacy = PharmacyAgent()
_billing = BillingAgent()
_discharge = DischargeAgent()


def build_workflow() -> StateGraph:
    """Build and return the compiled hospital workflow graph.

    Topology::

        START → supervisor ←→ {admission, insurance, doctor,
                                lab, pharmacy, billing, discharge}
        supervisor → END  (when FINISH is chosen)

    Each spoke agent returns a plain state-update dict (goes back to
    supervisor automatically because the supervisor is the only node
    that emits ``Command`` objects with ``goto``).
    """

    graph = StateGraph(HospitalState)

    # ── Register nodes ───────────────────────────────────────────
    graph.add_node("supervisor", _supervisor.run)
    graph.add_node("admission", _admission.run)
    graph.add_node("insurance", _insurance.run)
    graph.add_node("doctor", _doctor.run)
    graph.add_node("lab", _lab.run)
    graph.add_node("pharmacy", _pharmacy.run)
    graph.add_node("billing", _billing.run)
    graph.add_node("discharge", _discharge.run)

    # ── Entry edge ───────────────────────────────────────────────
    graph.add_edge(START, "supervisor")

    # ── Spoke → Hub edges (every agent returns to supervisor) ────
    graph.add_edge("admission", "supervisor")
    graph.add_edge("insurance", "supervisor")
    graph.add_edge("doctor", "supervisor")
    graph.add_edge("lab", "supervisor")
    graph.add_edge("pharmacy", "supervisor")
    graph.add_edge("billing", "supervisor")
    graph.add_edge("discharge", "supervisor")

    # Note: supervisor → spoke routing is handled dynamically via
    # Command(goto=...) inside SupervisorAgent.run().
    # supervisor → END is handled via Command(goto="__end__").

    return graph.compile()
