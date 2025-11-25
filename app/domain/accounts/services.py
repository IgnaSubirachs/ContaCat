from typing import List, Optional
from .entities import Account, AccountType
from .repositories import AccountRepository


class AccountService:
    """Application service for account-related use cases."""

    def __init__(self, repository: AccountRepository):
        self._repository = repository

    def create_account(
        self, 
        code: str, 
        name: str, 
        account_type: AccountType, 
        group: int,
        parent_code: Optional[str] = None
    ) -> None:
        """Use case: create a new account."""

        code = code.strip()
        name = name.strip()
        
        # Validate inputs
        if not code:
            raise ValueError("Account code cannot be empty.")
        if not name:
            raise ValueError("Account name cannot be empty.")
        if not isinstance(account_type, AccountType):
            raise ValueError(f"Invalid account type: {account_type}")

        existing = self._repository.find_by_code(code)
        if existing:
            raise ValueError(f"Account with code {code} already exists.")

        account = Account(
            code=code,
            name=name,
            account_type=account_type,
            group=group,
            parent_code=parent_code,
            is_active=True,
        )
        account.validate() # Domain validation
        
        self._repository.add(account)

    def list_accounts(self) -> List[Account]:
        """Use case: list all accounts."""
        return self._repository.list_all()

    def list_accounts_by_group(self, group: int) -> List[Account]:
        """Use case: list accounts by group."""
        return self._repository.list_by_group(group)

    def get_account_by_code(self, code: str) -> Optional[Account]:
        """Use case: get account by code."""
        return self._repository.find_by_code(code)
