from typing import List, Optional
from app.infrastructure.db.base import SessionLocal
from app.domain.treasury.entities import BankAccount
from app.infrastructure.persistence.treasury.models import BankAccountModel

class SqlAlchemyTreasuryRepository:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    def save(self, bank_account: BankAccount) -> None:
        with self.session_factory() as session:
            model = BankAccountModel(
                id=bank_account.id,
                name=bank_account.name,
                iban=bank_account.iban,
                bic=bank_account.bic,
                account_code=bank_account.account_code,
                currency=bank_account.currency,
                is_active=bank_account.is_active
            )
            session.merge(model)
            session.commit()

    def list_all(self) -> List[BankAccount]:
        with self.session_factory() as session:
            models = session.query(BankAccountModel).all()
            return [self._to_entity(m) for m in models]

    def get_by_id(self, id: str) -> Optional[BankAccount]:
        with self.session_factory() as session:
            model = session.query(BankAccountModel).get(id)
            if model:
                return self._to_entity(model)
            return None

    def _to_entity(self, model: BankAccountModel) -> BankAccount:
        return BankAccount(
            id=model.id,
            name=model.name,
            iban=model.iban,
            bic=model.bic,
            account_code=model.account_code,
            currency=model.currency,
            is_active=model.is_active
        )
