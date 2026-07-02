"""In-memory hospital data repository.

This is a lightweight stub that stores patient records in a plain dict.
It is designed to be replaced with a PostgreSQL-backed implementation
later without changing the public interface.
"""


class HospitalRepository:
    """Simple in-memory repository for patient data.

    Storage layout::

        _store = {
            "<patient_id>": {
                "_patient": { ... },       # core patient info
                "admission": { ... },      # section records
                "insurance": { ... },
                ...
            }
        }
    """

    def __init__(self) -> None:
        self._store: dict = {}

    # -- Patient helpers ------------------------------------------------

    def save_patient(self, patient_id: str, data: dict) -> None:
        """Create or update the core patient record."""
        self._store.setdefault(patient_id, {})
        self._store[patient_id]["_patient"] = data

    def get_patient(self, patient_id: str) -> dict | None:
        """Return the core patient record, or ``None`` if not found."""
        return self._store.get(patient_id, {}).get("_patient")

    # -- Section-level helpers ------------------------------------------

    def save_record(self, patient_id: str, section: str, data: dict) -> None:
        """Save a section record (e.g. admission, billing) for a patient."""
        self._store.setdefault(patient_id, {})
        self._store[patient_id][section] = data

    def get_record(self, patient_id: str, section: str) -> dict | None:
        """Return a single section record, or ``None`` if not found."""
        return self._store.get(patient_id, {}).get(section)

    def get_full_record(self, patient_id: str) -> dict | None:
        """Return the complete record for a patient, or ``None`` if not found."""
        return self._store.get(patient_id)
