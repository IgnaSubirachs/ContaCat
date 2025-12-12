from dataclasses import dataclass, field
from typing import Optional
import uuid

@dataclass
class BankAccount:
    """Represents a company bank account."""
    name: str  # e.g., "La Caixa Principal"
    iban: str
    bic: Optional[str] = None
    account_code: Optional[str] = None  # Accounting account (e.g., 57200001)
    currency: str = "EUR"
    is_active: bool = True
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
