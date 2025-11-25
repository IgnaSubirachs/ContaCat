from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Account

class AccountRepository(ABC):
    """Abstraction for account persistence."""

    @abstractmethod
    def add(self, account: Account) -> None:
        """Store a new account. Raises if duplicate code."""
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> List[Account]:
        """Return all accounts ordered by code."""
        raise NotImplementedError

    @abstractmethod
    def list_by_group(self, group: int) -> List[Account]:
        """Return accounts filtered by group."""
        raise NotImplementedError

    @abstractmethod
    def find_by_code(self, code: str) -> Optional[Account]:
        """Return an account by code, or None."""
        raise NotImplementedError