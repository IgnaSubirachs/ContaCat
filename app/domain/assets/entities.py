from datetime import date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class AssetStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SOLD = "SOLD"
    SCRAPPED = "SCRAPPED"
    FULLY_DEPRECIATED = "FULLY_DEPRECIATED"

class DepreciationMethod(str, Enum):
    LINEAR = "LINEAR"
    # Future methods: DECLINING_BALANCE, SUM_OF_YEARS_DIGITS

class DepreciationEntry(BaseModel):
    """Represents a single depreciation event (amortització)."""
    id: Optional[int] = None
    asset_id: int
    date: date
    amount: float
    accumulated_depreciation: float
    description: str
    journal_entry_id: Optional[int] = None  # Link to accounting

class Asset(BaseModel):
    """Represents a fixed asset (immobilitzat)."""
    id: Optional[int] = None
    code: str
    name: str
    description: Optional[str] = None
    
    purchase_date: date
    purchase_price: float
    
    useful_life_years: int
    residual_value: float = 0.0
    
    depreciation_method: DepreciationMethod = DepreciationMethod.LINEAR
    status: AssetStatus = AssetStatus.ACTIVE
    
    account_code_asset: str  # e.g., 211 (Construccions)
    account_code_accumulated_depreciation: str  # e.g., 281 (Amort. Acum. Construccions)
    account_code_depreciation_expense: str  # e.g., 681 (Amort. Immobilitzat Material)
    
    depreciation_entries: List[DepreciationEntry] = []

    @property
    def current_value(self) -> float:
        """Calculates current book value (Valor Comptable)."""
        total_depreciated = sum(entry.amount for entry in self.depreciation_entries)
        return self.purchase_price - total_depreciated

    @property
    def accumulated_depreciation(self) -> float:
        return sum(entry.amount for entry in self.depreciation_entries)
