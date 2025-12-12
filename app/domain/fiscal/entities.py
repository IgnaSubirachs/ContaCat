from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from enum import Enum


class FiscalYearStatus(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


@dataclass
class FiscalYear:
    """Represents a fiscal year/accounting period."""
    name: str
    start_date: date
    end_date: date
    status: FiscalYearStatus = FiscalYearStatus.OPEN
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def is_open(self) -> bool:
        return self.status == FiscalYearStatus.OPEN
    
    def contains_date(self, check_date: date) -> bool:
        """Check if a date falls within this fiscal year."""
        return self.start_date <= check_date <= self.end_date
    
    def __post_init__(self):
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
