from dataclasses import dataclass
from datetime import date
from typing import Optional, List
from decimal import Decimal
from enum import Enum
import uuid

from app.domain.accounts.entities import Account, AccountType


class JournalEntryStatus(Enum):
    """Status of journal entries."""
    DRAFT = "DRAFT"  # Esborrany
    POSTED = "POSTED"  # Comptabilitzat


@dataclass
class JournalLine:
    """Journal line entity (línia d'assentament)."""
    account_code: str  # Codi del compte
    debit: Decimal  # Deure
    credit: Decimal  # Haver
    description: str = ""
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        
        # Ensure Decimal type
        if not isinstance(self.debit, Decimal):
            self.debit = Decimal(str(self.debit))
        if not isinstance(self.credit, Decimal):
            self.credit = Decimal(str(self.credit))
    
    @property
    def amount(self) -> Decimal:
        """Get the amount (debit or credit, whichever is non-zero)."""
        return self.debit if self.debit > 0 else self.credit
    
    def validate(self) -> None:
        """Validate journal line."""
        if not self.account_code:
            raise ValueError("El codi del compte és obligatori")
        
        if self.debit < 0 or self.credit < 0:
            raise ValueError("El deure i haver no poden ser negatius")
        
        if self.debit > 0 and self.credit > 0:
            raise ValueError("Una línia no pot tenir deure i haver alhora")
        
        if self.debit == 0 and self.credit == 0:
            raise ValueError("Una línia ha de tenir deure o haver")


@dataclass
class JournalEntry:
    """Journal entry entity (assentament comptable)."""
    entry_number: int  # Número d'assentament
    entry_date: date  # Data de l'assentament
    description: str  # Descripció
    lines: List[JournalLine]  # Línies de l'assentament
    status: JournalEntryStatus = JournalEntryStatus.DRAFT
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
    
    @property
    def total_debit(self) -> Decimal:
        """Calculate total debit."""
        return sum(line.debit for line in self.lines)
    
    @property
    def total_credit(self) -> Decimal:
        """Calculate total credit."""
        return sum(line.credit for line in self.lines)
    
    @property
    def is_balanced(self) -> bool:
        """Check if entry is balanced (debit = credit)."""
        return self.total_debit == self.total_credit
    
    def validate(self) -> None:
        """Validate journal entry with double-entry bookkeeping rules."""
        if not self.description or len(self.description.strip()) == 0:
            raise ValueError("La descripció és obligatòria")
        
        if not self.lines or len(self.lines) < 2:
            raise ValueError("Un assentament ha de tenir almenys 2 línies")
        
        # Validate each line
        for line in self.lines:
            line.validate()
        
        # CRITICAL: Double-entry validation
        if not self.is_balanced:
            raise ValueError(
                f"L'assentament no està quadrat: "
                f"Deure={self.total_debit}, Haver={self.total_credit}"
            )
    
    def post(self) -> None:
        """Post the journal entry (make it permanent)."""
        self.validate()
        self.status = JournalEntryStatus.POSTED
    
    def can_edit(self) -> bool:
        """Check if entry can be edited."""
        return self.status == JournalEntryStatus.DRAFT
