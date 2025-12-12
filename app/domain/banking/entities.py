from datetime import datetime, date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class StatementStatus(str, Enum):
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    RECONCILED = "RECONCILED"

class BankStatementLine(BaseModel):
    id: Optional[str] = None
    statement_id: str
    date: date
    value_date: Optional[date] = None
    amount: float
    concept: str
    balance: Optional[float] = None
    reconciled_entry_id: Optional[str] = None # ID of the journal entry matched
    status: str = "PENDING" # PENDING, MATCHED

class BankStatement(BaseModel):
    id: Optional[str] = None
    account_id: str # Link to treasury.BankAccount or directly to an Account ID (572)
    filename: str
    upload_date: datetime = Field(default_factory=datetime.now)
    status: StatementStatus = StatementStatus.PENDING
    lines: List[BankStatementLine] = []
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
