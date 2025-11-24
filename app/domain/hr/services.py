from typing import List, Optional
from datetime import date
from decimal import Decimal
from app.domain.hr.entities import Employee
from app.domain.hr.repositories import EmployeeRepository


class EmployeeService:
    """Service for managing employees."""
    
    def __init__(self, repository: EmployeeRepository):
        self._repository = repository
    
    def create_employee(
        self,
        first_name: str,
        last_name: str,
        dni: str,
        email: str,
        phone: str,
        position: str,
        department: str,
        hire_date: date,
        salary: Decimal
    ) -> Employee:
        """Create a new employee."""
        # Check if DNI already exists
        existing = self._repository.find_by_dni(dni)
        if existing:
            raise ValueError(f"Ja existeix un empleat amb el DNI {dni}")
        
        # Create and validate employee
        employee = Employee(
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            email=email,
            phone=phone,
            position=position,
            department=department,
            hire_date=hire_date,
            salary=salary,
            is_active=True
        )
        employee.validate()
        
        # Save to repository
        self._repository.add(employee)
        return employee
    
    def update_employee(
        self,
        employee_id: str,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        position: str,
        department: str,
        salary: Decimal
    ) -> Employee:
        """Update an existing employee."""
        employee = self._repository.find_by_id(employee_id)
        if not employee:
            raise ValueError(f"No s'ha trobat l'empleat amb ID {employee_id}")
        
        # Update fields
        employee.first_name = first_name
        employee.last_name = last_name
        employee.email = email
        employee.phone = phone
        employee.position = position
        employee.department = department
        employee.salary = salary
        
        employee.validate()
        self._repository.update(employee)
        return employee
    
    def deactivate_employee(self, employee_id: str) -> None:
        """Deactivate an employee."""
        employee = self._repository.find_by_id(employee_id)
        if not employee:
            raise ValueError(f"No s'ha trobat l'empleat amb ID {employee_id}")
        
        employee.is_active = False
        self._repository.update(employee)
    
    def list_all_employees(self) -> List[Employee]:
        """List all employees."""
        return self._repository.list_all()
    
    def list_active_employees(self) -> List[Employee]:
        """List only active employees."""
        return self._repository.list_active()
    
    def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """Get an employee by ID."""
        return self._repository.find_by_id(employee_id)
    
    def delete_employee(self, employee_id: str) -> None:
        """Delete an employee."""
        employee = self._repository.find_by_id(employee_id)
        if not employee:
            raise ValueError(f"No s'ha trobat l'empleat amb ID {employee_id}")
        
        self._repository.delete(employee_id)
