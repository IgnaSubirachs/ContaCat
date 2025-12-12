from datetime import datetime, date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class LoanStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class AmortizationStatus(str, Enum):
    PENDING = "PENDING"
    POSTED = "POSTED"

class AmortizationEntry(BaseModel):
    id: Optional[str] = None
    loan_id: str
    installment_number: int
    due_date: date
    principal_payment: float
    interest_payment: float
    total_payment: float
    remaining_balance: float
    status: AmortizationStatus = AmortizationStatus.PENDING
    journal_entry_id: Optional[str] = None # Link to accounting

class Loan(BaseModel):
    id: Optional[str] = None
    name: str
    lender_partner_id: str # Bank/Lender Partner ID
    principal_amount: float
    interest_rate: float # Annual interest rate in %
    start_date: date
    duration_months: int
    description: Optional[str] = None
    status: LoanStatus = LoanStatus.ACTIVE
    amortization_schedule: List[AmortizationEntry] = []
    
    # Linked accounts for automation
    account_principal_long_term: str # e.g., 170
    account_principal_short_term: str # e.g., 520
    account_interest_expense: str # e.g., 662
    account_bank: str # e.g., 572
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
