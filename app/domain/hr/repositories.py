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
