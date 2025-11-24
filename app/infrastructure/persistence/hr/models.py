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
