from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.accounts.entities import Account
from app.domain.accounts.repositories import AccountRepository
from app.infrastructure.accounts.sqlalchemy_models import AccountModel
from app.infrastructure.db.base import SessionFactory


class SqlAlchemyAccountRepository(AccountRepository):
    """SQLAlchemy-based implementation of AccountRepository."""

    def __init__(self, session_factory: SessionFactory = SessionFactory):
        self._session_factory = session_factory

    def add(self, account: Account) -> None:
        session: Session = self._session_factory()
        try:
            model = AccountModel(
                code=account.code,
                name=account.name,
                account_type=account.account_type,
                is_active=account.is_active,
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

            return [
                Account(
                    code=m.code,
                    name=m.name,
                    account_type=m.account_type,
                    is_active=m.is_active,
                )
                for m in models
            ]
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
            return Account(
                code=model.code,
                name=model.name,
                account_type=model.account_type,
                is_active=model.is_active,
            )
        finally:
            session.close()
