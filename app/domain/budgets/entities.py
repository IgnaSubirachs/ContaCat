from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class BudgetStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"

class BudgetLine(BaseModel):
    id: Optional[str] = None
    budget_id: str
    account_group: str  # e.g., "6", "70", "628"
    amount: float

class Budget(BaseModel):
    id: Optional[str] = None
    name: str
    year: int
    description: Optional[str] = None
    status: BudgetStatus = BudgetStatus.DRAFT
    lines: List[BudgetLine] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def add_line(self, account_group: str, amount: float) -> BudgetLine:
        line = BudgetLine(
            budget_id=self.id if self.id else "",
            account_group=account_group,
            amount=amount
        )
        self.lines.append(line)
        return line
