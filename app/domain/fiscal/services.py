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

import re
from decimal import Decimal
from app.domain.accounting.repositories import JournalRepository
from app.domain.settings.services import SettingsService
from app.domain.fiscal.models import Model303Data

class FiscalModelService:
    """Service for calculating Fiscal Models (AEAT)."""
    
    def __init__(self, journal_repository: JournalRepository, settings_service: SettingsService):
        self._journal_repo = journal_repository
        self._settings_service = settings_service
        
    def calculate_model_303(self, year: int, period: str, start_date: date, end_date: date) -> Model303Data:
        """
        Calculate Model 303 (VAT) for a given period.
        It scans Journal Entries for accounts 477 (Output) and 472 (Input).
        """
        company_settings = self._settings_service.get_settings_or_default()
        
        model = Model303Data(
            year=year,
            period=period,
            company_name=company_settings.name,
            company_nif=company_settings.tax_id
        )
        
        # Get Journal Entries
        entries = self._journal_repo.list_by_date_range(start_date, end_date)
        
        # Regex for parsing rate from description: "IVA 21%..."
        rate_pattern = re.compile(r"IVA\s+(\d+)%", re.IGNORECASE)
        
        for entry in entries:
            # Skip non-posted? Official models usually based on posted.
            # But let's assume all listed are valid or check status. 
            # Repo list_by_date_range returns all.
            if entry.status.value != "POSTED":
                continue
                
            for line in entry.lines:
                code = line.account_code
                
                # OUTPUT VAT (Repercutit) - Account 477...
                if code.startswith("477"):
                    amount = line.credit - line.debit # Liability increases on Credit
                    # If amount is negative (refund?), handle accordingly.
                    
                    if amount == 0:
                        continue
                        
                    # Determine Rate
                    match = rate_pattern.search(line.description)
                    rate = int(match.group(1)) if match else 21 # Default to General
                    
                    if rate not in model.repercutit:
                         model.repercutit[rate].rate = rate # Should exist from post_init
                    
                    # Calculate Base (Reverse)
                    # Quota = Base * (Rate/100) => Base = Quota / (Rate/100)
                    base = amount / (Decimal(rate) / Decimal(100))
                    
                    model.repercutit[rate].add(base, amount)
                    
                # INPUT VAT (Suportat) - Account 472...
                elif code.startswith("472"):
                    amount = line.debit - line.credit # Asset increases on Debit
                    
                    if amount == 0:
                        continue

                    match = rate_pattern.search(line.description)
                    rate = int(match.group(1)) if match else 21
                    
                    if rate not in model.suportat:
                        model.suportat[rate].rate = rate
                        
                    base = amount / (Decimal(rate) / Decimal(100))
                    
                    model.suportat[rate].add(base, amount)
        
        model.calculate_totals()
        return model
