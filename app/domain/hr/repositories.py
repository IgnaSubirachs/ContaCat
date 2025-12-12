from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.hr.entities import Employee


class EmployeeRepository(ABC):
    """Abstract repository for Employee entities."""
    
    @abstractmethod
    def add(self, employee: Employee) -> None:
        """Add a new employee."""
        pass
    
    @abstractmethod
    def update(self, employee: Employee) -> None:
        """Update an existing employee."""
        pass
    
    @abstractmethod
    def list_all(self) -> List[Employee]:
        """List all employees."""
        pass
    
    @abstractmethod
    def list_active(self) -> List[Employee]:
        """List only active employees."""
        pass
    
    @abstractmethod
    def find_by_id(self, employee_id: str) -> Optional[Employee]:
        """Find an employee by ID."""
        pass
    
    @abstractmethod
    def find_by_dni(self, dni: str) -> Optional[Employee]:
        """Find an employee by DNI."""
        pass
    
    @abstractmethod
    def delete(self, employee_id: str) -> None:
        """Delete an employee."""
        pass


class PayrollRepository(ABC):
    """Abstract repository for Payroll entities."""
    
    @abstractmethod
    def add(self, payroll: 'Payroll') -> None:
        """Add a new payroll."""
        pass
    
    @abstractmethod
    def update(self, payroll: 'Payroll') -> None:
        """Update an existing payroll."""
        pass
    
    @abstractmethod
    def find_by_id(self, payroll_id: str) -> Optional['Payroll']:
        """Find a payroll by ID."""
        pass
    
    @abstractmethod
    def list_by_employee(self, employee_id: str) -> List['Payroll']:
        """List payrolls for an employee."""
        pass
    
    @abstractmethod
    def list_by_period(self, month: int, year: int) -> List['Payroll']:
        """List payrolls for a specific month/year."""
        pass
