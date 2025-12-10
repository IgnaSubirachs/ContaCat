from sqlalchemy import String, Boolean, Integer, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from decimal import Decimal

from app.infrastructure.db.base import Base


class EmployeeModel(Base):
    """SQLAlchemy model for employees table."""
    __tablename__ = "employees"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dni: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    position: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    salary: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Labor compliance fields
    nss: Mapped[str] = mapped_column(String(20), default="")
    contract_type: Mapped[str] = mapped_column(String(50), default="INDEFINITE")
    contract_start_date: Mapped[date] = mapped_column(Date, nullable=True)
    contract_end_date: Mapped[date] = mapped_column(Date, nullable=True)
    work_schedule: Mapped[str] = mapped_column(String(50), default="FULL_TIME")
    weekly_hours: Mapped[int] = mapped_column(Integer, default=40)
    professional_category: Mapped[str] = mapped_column(String(100), default="")
    social_security_group: Mapped[int] = mapped_column(Integer, default=7)
    
    # Family situation
    marital_status: Mapped[str] = mapped_column(String(50), default="SINGLE")
    children_count: Mapped[int] = mapped_column(Integer, default=0)
    disability_degree: Mapped[int] = mapped_column(Integer, default=0)
    
    # Salary details
    base_salary: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    salary_supplements: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    irpf_retention: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    
    # Vacation
    annual_vacation_days: Mapped[int] = mapped_column(Integer, default=22)

    def __repr__(self) -> str:
        return f"<EmployeeModel {self.dni} - {self.first_name} {self.last_name}>"


class PayrollModel(Base):
    """SQLAlchemy model for payrolls table."""
    __tablename__ = "payrolls"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(36), index=True)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Salary components
    gross_salary: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    base_salary: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    supplements: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    
    # Deductions
    social_security_employee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    social_security_company: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    irpf_base: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    irpf_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    irpf_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    net_salary: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Metadata
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    working_days: Mapped[int] = mapped_column(Integer, default=30)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT")
    
    def __repr__(self) -> str:
        return f"<PayrollModel {self.year}-{self.month} emp={self.employee_id}>"
