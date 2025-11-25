from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.accounts.entities import Account, AccountType
from app.domain.accounts.repositories import AccountRepository
from app.infrastructure.persistence.accounts.models import AccountModel
from app.infrastructure.db.base import SessionLocal


class SqlAlchemyAccountRepository(AccountRepository):
    """SQLAlchemy-based implementation of AccountRepository."""

    def __init__(self, session_factory=SessionLocal):
        self._session_factory = session_factory

    def add(self, account: Account) -> None:
        session: Session = self._session_factory()
        try:
            model = AccountModel(
                id=account.id,
                code=account.code,
                name=account.name,
                account_type=account.account_type,
                group=account.group,
                is_active=account.is_active,
                parent_code=account.parent_code
            )
            session.add(model)
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Account with code {account.code} already exists.")
        finally:
            session.close()

    def list_all(self) -> List[Account]:
        session: Session = self._session_factory()
        try:
            stmt = select(AccountModel).order_by(AccountModel.code)
            result = session.execute(stmt)
            models: List[AccountModel] = result.scalars().all()
            return [self._model_to_entity(m) for m in models]
        finally:
            session.close()

    def list_by_group(self, group: int) -> List[Account]:
        session: Session = self._session_factory()
        try:
            stmt = select(AccountModel).where(
                AccountModel.group == group,
                AccountModel.is_active == True
            ).order_by(AccountModel.code)
            result = session.execute(stmt)
            models: List[AccountModel] = result.scalars().all()
            return [self._model_to_entity(m) for m in models]
        finally:
            session.close()

    def find_by_code(self, code: str) -> Optional[Account]:
        session: Session = self._session_factory()
        try:
            stmt = select(AccountModel).where(AccountModel.code == code)
            result = session.execute(stmt)
            model: AccountModel | None = result.scalars().first()
            if not model:
                return None
            return self._model_to_entity(model)
        finally:
            session.close()

    def _model_to_entity(self, model: AccountModel) -> Account:
        return Account(
            id=model.id,
            code=model.code,
            name=model.name,
            account_type=AccountType(model.account_type) if isinstance(model.account_type, str) else model.account_type,
            group=model.group,
            is_active=model.is_active,
            parent_code=model.parent_code
        )
