from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.domain.banking.entities import BankStatement, BankStatementLine
from app.domain.banking.repositories import BankStatementRepository
from app.infrastructure.persistence.banking.models import BankStatementModel, BankStatementLineModel

class SqlAlchemyBankStatementRepository(BankStatementRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: BankStatementModel) -> BankStatement:
        lines = []
        if model.lines:
            for item in model.lines:
                lines.append(BankStatementLine(
                    id=item.id,
                    statement_id=item.statement_id,
                    date=item.date,
                    amount=item.amount,
                    concept=item.concept,
                    balance=item.balance,
                    reconciled_entry_id=item.reconciled_entry_id,
                    status=item.status
                ))
        
        return BankStatement(
            id=model.id,
            account_id=model.account_id,
            filename=model.filename,
            upload_date=model.upload_date,
            status=model.status,
            lines=lines,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def save(self, statement: BankStatement) -> BankStatement:
        model = self.session.query(BankStatementModel).filter_by(id=statement.id).first()
        
        if not model:
            model = BankStatementModel(id=statement.id)
            self.session.add(model)
            
        model.account_id = statement.account_id
        model.filename = statement.filename
        model.status = statement.status
        model.updated_at = statement.updated_at
        
        # Handle lines (usually only add/update status, not remove in this simple case)
        # But for new uploads, we need to add all lines
        
        existing_ids = {l.id for l in model.lines}
        
        for line in statement.lines:
            if line.id not in existing_ids:
                line_model = BankStatementLineModel(
                    id=line.id,
                    statement_id=model.id,
                    date=line.date,
                    amount=line.amount,
                    concept=line.concept,
                    balance=line.balance,
                    status=line.status,
                    reconciled_entry_id=line.reconciled_entry_id
                )
                self.session.add(line_model)
            else:
                # Update existing (e.g. status)
                line_model = next(l for l in model.lines if l.id == line.id)
                line_model.status = line.status
                line_model.reconciled_entry_id = line.reconciled_entry_id
        
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, statement_id: str) -> Optional[BankStatement]:
        model = self.session.query(BankStatementModel).options(joinedload(BankStatementModel.lines)).filter_by(id=statement_id).first()
        if model:
            return self._to_entity(model)
        return None

    def list_all(self) -> List[BankStatement]:
        models = self.session.query(BankStatementModel).options(joinedload(BankStatementModel.lines)).order_by(BankStatementModel.upload_date.desc()).all()
        return [self._to_entity(m) for m in models]

    def delete(self, statement_id: str) -> bool:
        model = self.session.query(BankStatementModel).filter_by(id=statement_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
