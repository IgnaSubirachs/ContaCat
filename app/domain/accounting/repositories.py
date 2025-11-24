from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from app.domain.accounting.entities import Account, JournalEntry


class AccountRepository(ABC):
    """Abstract repository for accounts."""
    
    @abstractmethod
    def add(self, account: Account) -> None:
        """Add a new account."""
        pass
    
    @abstractmethod
    def find_by_code(self, code: str) -> Optional[Account]:
        """Find account by code."""
        pass
    
    @abstractmethod
    def list_all(self) -> List[Account]:
        """List all accounts."""
        pass
    
    @abstractmethod
    def list_by_group(self, group: int) -> List[Account]:
        """List accounts by group."""
        pass
    
    @abstractmethod
    def update(self, account: Account) -> None:
        """Update an account."""
        pass


class JournalRepository(ABC):
    """Abstract repository for journal entries."""
    
    @abstractmethod
    def add(self, entry: JournalEntry) -> None:
        """Add a new journal entry."""
        pass
    
    @abstractmethod
    def find_by_id(self, entry_id: str) -> Optional[JournalEntry]:
        """Find journal entry by ID."""
        pass
    
    @abstractmethod
    def find_by_number(self, entry_number: int) -> Optional[JournalEntry]:
        """Find journal entry by number."""
        pass
    
    @abstractmethod
    def list_all(self) -> List[JournalEntry]:
        """List all journal entries."""
        pass
    
    @abstractmethod
    def list_by_date_range(self, start_date: date, end_date: date) -> List[JournalEntry]:
        """List journal entries in date range."""
        pass
    
    @abstractmethod
    def get_next_entry_number(self) -> int:
        """Get next available entry number."""
        pass
    
    @abstractmethod
    def update(self, entry: JournalEntry) -> None:
        """Update a journal entry."""
        pass
    
    @abstractmethod
    def delete(self, entry_id: str) -> None:
        """Delete a journal entry (only if DRAFT)."""
        pass
