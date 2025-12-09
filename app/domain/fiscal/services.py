from datetime import date
from typing import List, Optional
from app.domain.fiscal.entities import FiscalYear, FiscalYearStatus
from app.domain.fiscal.repositories import FiscalYearRepository


class FiscalYearService:
    """Service for fiscal year management."""
    
    def __init__(self, repository: FiscalYearRepository):
        self._repository = repository
    
    def create_fiscal_year(
        self, 
        name: str, 
        start_date: date, 
        end_date: date
    ) -> FiscalYear:
        """Create a new fiscal year."""
        # Check if name already exists
        existing = self._repository.get_by_name(name)
        if existing:
            raise ValueError(f"Fiscal year '{name}' already exists")
        
        # Check for overlapping dates
        all_years = self._repository.list_all()
        for year in all_years:
            if (start_date <= year.end_date and end_date >= year.start_date):
                raise ValueError(f"Date range overlaps with fiscal year '{year.name}'")
        
        fiscal_year = FiscalYear(
            name=name,
            start_date=start_date,
            end_date=end_date,
            status=FiscalYearStatus.OPEN
        )
        
        return self._repository.add(fiscal_year)
    
    def close_fiscal_year(self, fiscal_year_id: int) -> FiscalYear:
        """Close a fiscal year (no more operations allowed)."""
        fiscal_year = self._repository.get_by_id(fiscal_year_id)
        if not fiscal_year:
            raise ValueError("Fiscal year not found")
        
        if fiscal_year.status == FiscalYearStatus.CLOSED:
            raise ValueError("Fiscal year is already closed")
        
        fiscal_year.status = FiscalYearStatus.CLOSED
        return self._repository.update(fiscal_year)
    
    def reopen_fiscal_year(self, fiscal_year_id: int) -> FiscalYear:
        """Reopen a closed fiscal year (admin only)."""
        fiscal_year = self._repository.get_by_id(fiscal_year_id)
        if not fiscal_year:
            raise ValueError("Fiscal year not found")
        
        if fiscal_year.status == FiscalYearStatus.OPEN:
            raise ValueError("Fiscal year is already open")
        
        fiscal_year.status = FiscalYearStatus.OPEN
        return self._repository.update(fiscal_year)
    
    def get_current_fiscal_year(self) -> Optional[FiscalYear]:
        """Get the currently open fiscal year."""
        return self._repository.get_current()
    
    def get_fiscal_year_for_date(self, check_date: date) -> Optional[FiscalYear]:
        """Get fiscal year for a specific date."""
        return self._repository.get_by_date(check_date)
    
    def validate_date_in_open_year(self, check_date: date) -> bool:
        """Check if date is within an open fiscal year."""
        fiscal_year = self._repository.get_by_date(check_date)
        return fiscal_year is not None and fiscal_year.is_open()
    
    def list_all(self) -> List[FiscalYear]:
        """List all fiscal years."""
        return self._repository.list_all()
    
    def get_by_id(self, fiscal_year_id: int) -> Optional[FiscalYear]:
        """Get fiscal year by ID."""
        return self._repository.get_by_id(fiscal_year_id)
