from dataclasses import dataclass
from datetime import date
from typing import Optional
from decimal import Decimal
import uuid


@dataclass
class Employee:
    """Employee entity representing a company employee."""
    first_name: str
    last_name: str
    dni: str  # DNI/NIE
    email: str
    phone: str
    position: str  # Càrrec
    department: str  # Departament
    hire_date: date  # Data d'alta
    salary: Decimal  # Salari brut mensual
    is_active: bool = True
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
    
    @property
    def full_name(self) -> str:
        """Return full name."""
        return f"{self.first_name} {self.last_name}"
    
    def validate(self) -> None:
        """Validate employee data."""
        if not self.first_name or len(self.first_name.strip()) == 0:
            raise ValueError("El nom és obligatori")
        if not self.last_name or len(self.last_name.strip()) == 0:
            raise ValueError("Els cognoms són obligatoris")
        if not self.dni or len(self.dni.strip()) == 0:
            raise ValueError("El DNI/NIE és obligatori")
        if not self.email or len(self.email.strip()) == 0:
            raise ValueError("L'email és obligatori")
        if not self.position or len(self.position.strip()) == 0:
            raise ValueError("El càrrec és obligatori")
        if not self.department or len(self.department.strip()) == 0:
            raise ValueError("El departament és obligatori")
        if self.salary <= 0:
            raise ValueError("El salari ha de ser superior a 0")
