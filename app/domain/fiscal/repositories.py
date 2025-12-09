from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from app.domain.fiscal.entities import FiscalYear


class FiscalYearRepository(ABC):
    """Abstract repository for fiscal year operations."""
    
    @abstractmethod
    def add(self, fiscal_year: FiscalYear) -> FiscalYear:
        """Add a new fiscal year."""
        pass
    
    @abstractmethod
    def get_by_id(self, fiscal_year_id: int) -> Optional[FiscalYear]:
        """Get fiscal year by ID."""
        pass
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[FiscalYear]:
        """Get fiscal year by name (e.g., '2024')."""
        pass
    
    @abstractmethod
    def get_current(self) -> Optional[FiscalYear]:
        """Get the currently open fiscal year."""
        pass
    
    @abstractmethod
    def get_by_date(self, check_date: date) -> Optional[FiscalYear]:
        """Get fiscal year containing a specific date."""
        pass
    
    @abstractmethod
    def list_all(self) -> List[FiscalYear]:
        """List all fiscal years ordered by start_date desc."""
        pass
    
    @abstractmethod
    def update(self, fiscal_year: FiscalYear) -> FiscalYear:
        """Update an existing fiscal year."""
        pass
