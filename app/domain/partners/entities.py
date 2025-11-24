from dataclasses import dataclass
from typing import Optional
import uuid

@dataclass
class Partner:
    """Partner entity representing a customer or supplier."""
    name: str
    tax_id: str
    email: str
    phone: str
    is_supplier: bool
    is_customer: bool
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
    
    def validate(self) -> None:
        """Validate partner data."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("El nom del partner és obligatori")
        if not self.tax_id or len(self.tax_id.strip()) == 0:
            raise ValueError("El NIF/CIF és obligatori")
        if not self.is_supplier and not self.is_customer:
            raise ValueError("El partner ha de ser client, proveïdor o ambdós")
