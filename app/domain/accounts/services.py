from typing import List
from .entities import Account
from .repositories import AccountRepository


class AccountService:
    """Application service for account-related use cases."""

    VALID_TYPES = {"asset", "liability", "equity", "income", "expense"}

    def __init__(self, repository: AccountRepository):
        self._repository = repository

    def create_account(self, code: str, name: str, account_type: str) -> None:
        """Use case: create a new account."""

        code = code.strip()
        name = name.strip()
        account_type = account_type.strip().lower()

        if not code:
            raise ValueError("Account code cannot be empty.")
        if not name:
            raise ValueError("Account name cannot be empty.")
        if account_type not in self.VALID_TYPES:
            raise ValueError(f"Invalid account type: {account_type}")

        existing = self._repository.find_by_code(code)
        if existing:
            raise ValueError(f"Account with code {code} already exists.")

        account = Account(
            code=code,
            name=name,
            account_type=account_type,
            is_active=True,
        )
        self._repository.add(account)

    def get_chart_of_accounts(self) -> List[Account]:
        """Use case: list chart of accounts."""
        return self._repository.list_all()
