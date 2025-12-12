from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Dict
from decimal import Decimal
import uuid

from app.domain.validators.nif_cif_validator import DocumentValidator
from app.domain.validators.nss_validator import NSSValidator
from app.domain.validators.irpf_calculator import IRPFCalculator
from app.domain.hr.social_security import SocialSecurityCalculator




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
    
    # Labor compliance fields
    nss: str = ""  # Número Seguretat Social
    contract_type: str = "INDEFINITE"  # INDEFINITE, TEMPORARY, TRAINING, INTERNSHIP
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    work_schedule: str = "FULL_TIME"  # FULL_TIME, PART_TIME
    weekly_hours: int = 40
    professional_category: str = ""
    social_security_group: int = 7  # Grups 1-11
    
    # Family situation
    marital_status: str = "SINGLE"  # SINGLE, MARRIED, DIVORCED, WIDOWED
    children_count: int = 0
    disability_degree: int = 0  # 0, 33, 65
    
    # Salary details
    base_salary: Decimal = Decimal("0")
    salary_supplements: Decimal = Decimal("0")
    irpf_retention: Decimal = Decimal("0")  # Percentatge
    
    # Vacation
    annual_vacation_days: int = 22  # Dies laborables per any
    
    is_active: bool = True
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        
        # Set contract start date to hire date if not provided
        if self.contract_start_date is None:
            self.contract_start_date = self.hire_date
        
        # Calculate base salary if not provided (assume salary is total)
        if self.base_salary == 0:
            self.base_salary = self.salary
        
        # Auto-calculate IRPF if not provided
        if self.irpf_retention == 0:
            self.irpf_retention = self.calculate_irpf()
    
    @property
    def full_name(self) -> str:
        """Return full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def annual_salary(self) -> Decimal:
        """Calculate annual gross salary (12 months)."""
        return self.salary * 12
    
    @property
    def net_salary(self) -> Decimal:
        """Calculate net monthly salary after IRPF."""
        retention_amount = (self.salary * self.irpf_retention / 100).quantize(Decimal("0.01"))
        return self.salary - retention_amount
    
    @property
    def formatted_nss(self) -> str:
        """Return formatted NSS."""
        if not self.nss:
            return ""
        return NSSValidator.format_nss(self.nss)
    
    def calculate_irpf(self) -> Decimal:
        """Calculate IRPF retention percentage."""
        return IRPFCalculator.calculate_retention(
            annual_salary=self.annual_salary,
            children_count=self.children_count,
            disability_degree=self.disability_degree,
            marital_status=self.marital_status
        )
    
    def validate(self) -> None:
        """Validate employee data."""
        # Basic validations
        if not self.first_name or len(self.first_name.strip()) == 0:
            raise ValueError("El nom és obligatori")
        if not self.last_name or len(self.last_name.strip()) == 0:
            raise ValueError("Els cognoms són obligatoris")
        
        # Validate DNI/NIE
        if not self.dni or len(self.dni.strip()) == 0:
            raise ValueError("El DNI/NIE és obligatori")
        
        is_valid, doc_type = DocumentValidator.validate_document(self.dni)
        if not is_valid and doc_type not in ["PASSPORT"]:
            raise ValueError(f"El DNI/NIE '{self.dni}' no és vàlid")
        
        # Validate NSS if provided
        if self.nss and self.nss.strip():
            if not NSSValidator.validate_nss(self.nss):
                raise ValueError(f"El NSS '{self.nss}' no és vàlid")
        
        if not self.email or len(self.email.strip()) == 0:
            raise ValueError("L'email és obligatori")
        if not self.position or len(self.position.strip()) == 0:
            raise ValueError("El càrrec és obligatori")
        if not self.department or len(self.department.strip()) == 0:
            raise ValueError("El departament és obligatori")
        if self.salary <= 0:
            raise ValueError("El salari ha de ser superior a 0")
        
        # Validate contract dates
        if self.contract_end_date and self.contract_start_date:
            if self.contract_end_date < self.contract_start_date:
                raise ValueError("La data de fi del contracte no pot ser anterior a la data d'inici")
        
        # Validate weekly hours
        if self.weekly_hours < 0 or self.weekly_hours > 40:
            raise ValueError("Les hores setmanals han d'estar entre 0 i 40")
        
        # Validate social security group
        if self.social_security_group < 1 or self.social_security_group > 11:
            raise ValueError("El grup de cotització ha d'estar entre 1 i 11")
        
        # Validate children count
        if self.children_count < 0:
            raise ValueError("El nombre de fills no pot ser negatiu")
        
        # Validate disability degree
        if self.disability_degree not in [0, 33, 65]:
            raise ValueError("El grau de discapacitat ha de ser 0, 33 o 65")


from enum import Enum

class PayrollStatus(str, Enum):
    DRAFT = "DRAFT"
    PAID = "PAID"

@dataclass
class Payroll:
    """Payroll entity representing a monthly payslip."""
    employee_id: str
    month: int
    year: int
    gross_salary: Decimal  # Salari brut
    base_salary: Decimal   # Salari base
    supplements: Decimal   # Complements
    
    # Deductions
    social_security_employee: Decimal # Quota obrera (Treballador)
    social_security_company: Decimal  # Quota patronal (Empresa) - Informativa a nòmina
    irpf_base: Decimal     # Base IRPF
    irpf_rate: Decimal     # Tipus IRPF (%)
    irpf_amount: Decimal   # Import IRPF
    
    net_salary: Decimal    # Líquid a percebre
    
    # Metadata
    period_start: date
    period_end: date
    working_days: int = 30
    
    status: PayrollStatus = PayrollStatus.DRAFT
    id: Optional[str] = None
    
    # Calculated on retrieval if needed, not persisted directly if lazy
    employee: Optional[Employee] = None 
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
            
    def validate(self) -> None:
        """Validate payroll data."""
        if self.gross_salary < 0:
            raise ValueError("El salari brut no pot ser negatiu")
        if self.net_salary < 0:
            raise ValueError("El salari net no pot ser negatiu")
        if not (1 <= self.month <= 12):
            raise ValueError("El mes ha de ser entre 1 i 12")
        if self.year < 2000:
            raise ValueError("L'any no és vàlid")
