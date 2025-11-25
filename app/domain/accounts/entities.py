from dataclasses import dataclass
from enum import Enum
from typing import Optional
import uuid

class AccountType(Enum):
    """Types of accounts according to Spanish accounting."""
    ASSET = "ASSET"  # Actiu
    LIABILITY = "LIABILITY"  # Passiu
    EQUITY = "EQUITY"  # Patrimoni net
    INCOME = "INCOME"  # Ingressos
    EXPENSE = "EXPENSE"  # Despeses

@dataclass
class Account:
    code: str
    name: str
    account_type: AccountType
    group: int
    is_active: bool = True
    parent_code: Optional[str] = None
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())

    @property
    def is_debit_account(self) -> bool:
        """Check if account normally has debit balance."""
        return self.account_type in [AccountType.ASSET, AccountType.EXPENSE]
    
    @property
    def is_credit_account(self) -> bool:
        """Check if account normally has credit balance."""
        return self.account_type in [AccountType.LIABILITY, AccountType.EQUITY, AccountType.INCOME]

    def validate(self) -> None:
        """Validate account data."""
        if not self.code or len(self.code.strip()) == 0:
            raise ValueError("El codi del compte és obligatori")
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("El nom del compte és obligatori")
        
        if self.group < 1 or self.group > 9:
            raise ValueError("El grup ha d'estar entre 1 i 9")
        
        if not self.code.isdigit():
            raise ValueError("El codi del compte ha de ser numèric")