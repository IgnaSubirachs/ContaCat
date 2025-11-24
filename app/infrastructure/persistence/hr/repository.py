from typing import List, Optional
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.hr.entities import Employee
from app.domain.hr.repositories import EmployeeRepository
from app.infrastructure.persistence.hr.models import EmployeeModel
from app.infrastructure.db.base import SessionLocal


class SqlAlchemyEmployeeRepository(EmployeeRepository):
    """SQLAlchemy-based implementation of EmployeeRepository."""

    def __init__(self, session_factory=SessionLocal):
        self._session_factory = session_factory

    def add(self, employee: Employee) -> None:
        session: Session = self._session_factory()
        try:
            model = self._entity_to_model(employee)
            session.add(model)
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Ja existeix un empleat amb el DNI {employee.dni}")
        finally:
            session.close()

    def update(self, employee: Employee) -> None:
        session: Session = self._session_factory()
        try:
            stmt = select(EmployeeModel).where(EmployeeModel.id == employee.id)
            result = session.execute(stmt)
            model: EmployeeModel | None = result.scalars().first()
            
            if not model:
                raise ValueError(f"No s'ha trobat l'empleat amb ID {employee.id}")
            
            # Update all fields
            model.first_name = employee.first_name
            model.last_name = employee.last_name
            model.email = employee.email
            model.phone = employee.phone
            model.position = employee.position
            model.department = employee.department
            model.salary = employee.salary
            model.is_active = employee.is_active
            model.nss = employee.nss
            model.contract_type = employee.contract_type
            model.contract_start_date = employee.contract_start_date
            model.contract_end_date = employee.contract_end_date
            model.work_schedule = employee.work_schedule
            model.weekly_hours = employee.weekly_hours
            model.professional_category = employee.professional_category
            model.social_security_group = employee.social_security_group
            model.marital_status = employee.marital_status
            model.children_count = employee.children_count
            model.disability_degree = employee.disability_degree
            model.base_salary = employee.base_salary
            model.salary_supplements = employee.salary_supplements
            model.irpf_retention = employee.irpf_retention
            model.annual_vacation_days = employee.annual_vacation_days
            
            session.commit()
        finally:
            session.close()

    def list_all(self) -> List[Employee]:
        session: Session = self._session_factory()
        try:
            stmt = select(EmployeeModel).order_by(EmployeeModel.last_name, EmployeeModel.first_name)
            result = session.execute(stmt)
            models: List[EmployeeModel] = result.scalars().all()
            return [self._model_to_entity(m) for m in models]
        finally:
            session.close()

    def list_active(self) -> List[Employee]:
        session: Session = self._session_factory()
        try:
            stmt = select(EmployeeModel).where(EmployeeModel.is_active == True).order_by(
                EmployeeModel.last_name, EmployeeModel.first_name
            )
            result = session.execute(stmt)
            models: List[EmployeeModel] = result.scalars().all()
            return [self._model_to_entity(m) for m in models]
        finally:
            session.close()

    def find_by_id(self, employee_id: str) -> Optional[Employee]:
        session: Session = self._session_factory()
        try:
            stmt = select(EmployeeModel).where(EmployeeModel.id == employee_id)
            result = session.execute(stmt)
            model: EmployeeModel | None = result.scalars().first()
            if not model:
                return None
            return self._model_to_entity(model)
        finally:
            session.close()

    def find_by_dni(self, dni: str) -> Optional[Employee]:
        session: Session = self._session_factory()
        try:
            stmt = select(EmployeeModel).where(EmployeeModel.dni == dni)
            result = session.execute(stmt)
            model: EmployeeModel | None = result.scalars().first()
            if not model:
                return None
            return self._model_to_entity(model)
        finally:
            session.close()
    
    def delete(self, employee_id: str) -> None:
        session: Session = self._session_factory()
        try:
            stmt = select(EmployeeModel).where(EmployeeModel.id == employee_id)
            result = session.execute(stmt)
            model: EmployeeModel | None = result.scalars().first()
            
            if not model:
                raise ValueError(f"No s'ha trobat l'empleat amb ID {employee_id}")
            
            session.delete(model)
            session.commit()
        finally:
            session.close()

    def _model_to_entity(self, model: EmployeeModel) -> Employee:
        """Convert SQLAlchemy model to domain entity."""
        return Employee(
            id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            dni=model.dni,
            email=model.email,
            phone=model.phone,
            position=model.position,
            department=model.department,
            hire_date=model.hire_date,
            salary=model.salary,
            is_active=model.is_active,
            nss=model.nss,
            contract_type=model.contract_type,
            contract_start_date=model.contract_start_date,
            contract_end_date=model.contract_end_date,
            work_schedule=model.work_schedule,
            weekly_hours=model.weekly_hours,
            professional_category=model.professional_category,
            social_security_group=model.social_security_group,
            marital_status=model.marital_status,
            children_count=model.children_count,
            disability_degree=model.disability_degree,
            base_salary=model.base_salary,
            salary_supplements=model.salary_supplements,
            irpf_retention=model.irpf_retention,
            annual_vacation_days=model.annual_vacation_days,
        )
    
    def _entity_to_model(self, employee: Employee) -> EmployeeModel:
        """Convert domain entity to SQLAlchemy model."""
        return EmployeeModel(
            id=employee.id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            dni=employee.dni,
            email=employee.email,
            phone=employee.phone,
            position=employee.position,
            department=employee.department,
            hire_date=employee.hire_date,
            salary=employee.salary,
            is_active=employee.is_active,
            nss=employee.nss,
            contract_type=employee.contract_type,
            contract_start_date=employee.contract_start_date,
            contract_end_date=employee.contract_end_date,
            work_schedule=employee.work_schedule,
            weekly_hours=employee.weekly_hours,
            professional_category=employee.professional_category,
            social_security_group=employee.social_security_group,
            marital_status=employee.marital_status,
            children_count=employee.children_count,
            disability_degree=employee.disability_degree,
            base_salary=employee.base_salary,
            salary_supplements=employee.salary_supplements,
            irpf_retention=employee.irpf_retention,
            annual_vacation_days=employee.annual_vacation_days,
        )
