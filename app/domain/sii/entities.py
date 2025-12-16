"""SII submission tracking entity."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class SIIStatus(str, Enum):
    """SII submission status."""
    PENDING = "PENDING"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    ERROR = "ERROR"


@dataclass
class SIISubmission:
    """SII submission record."""
    invoice_id: str
    submission_date: datetime
    status: SIIStatus
    csv: Optional[str] = None  # Código Seguro de Verificación
    aeat_response: Optional[str] = None
    error_message: Optional[str] = None
    id: Optional[str] = None
