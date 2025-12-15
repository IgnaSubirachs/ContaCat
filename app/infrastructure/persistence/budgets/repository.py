from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.domain.budgets.entities import Budget, BudgetLine
from app.domain.budgets.repositories import BudgetRepository
from app.infrastructure.persistence.budgets.models import BudgetModel, BudgetLineModel

class SqlAlchemyBudgetRepository(BudgetRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: BudgetModel) -> Budget:
        budget = Budget(
            id=model.id,
            name=model.name,
            year=model.year,
            description=model.description,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
        # Manually map lines
        if model.lines:
            budget.lines = [
                BudgetLine(
                    id=line.id,
                    budget_id=line.budget_id,
                    account_group=line.account_group,
                    amount=line.amount
                ) for line in model.lines
            ]
        return budget

    def save(self, budget: Budget) -> Budget:
        # Check if exists
        model = self.session.query(BudgetModel).filter_by(id=budget.id).first()
        
        if not model:
            model = BudgetModel(id=budget.id)
            self.session.add(model)
        
        # Update fields
        model.name = budget.name
        model.year = budget.year
        model.description = budget.description
        model.status = budget.status
        model.updated_at = budget.updated_at
        
        # Determine lines to add/update/remove is complex, 
        # for simplicity in this MVP, we can clear and re-add if needed, 
        # or just handle additions. 
        # Let's try to map the current lines from entity to model.
        
        # Current strategy: Replace all lines. 
        # (Warning: inefficient for large data, but fine for budgets)
        # First, remove lines not in the new budget
        current_line_ids = {line.id for line in budget.lines if line.id}
        for existing_line in model.lines:
            if existing_line.id not in current_line_ids:
                self.session.delete(existing_line)
        
        # Update or Add lines
        for line_entity in budget.lines:
            line_model = next((l for l in model.lines if l.id == line_entity.id), None)
            if not line_model:
                line_model = BudgetLineModel(
                    id=line_entity.id,  # Should use the ID generated in service
                    budget_id=model.id,
                    account_group=line_entity.account_group,
                    amount=line_entity.amount
                )
                self.session.add(line_model)
            else:
                line_model.account_group = line_entity.account_group
                line_model.amount = line_entity.amount
        
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, budget_id: str) -> Optional[Budget]:
        model = self.session.query(BudgetModel).options(joinedload(BudgetModel.lines)).filter_by(id=budget_id).first()
        if model:
            return self._to_entity(model)
        return None

    def list_all(self) -> List[Budget]:
        models = self.session.query(BudgetModel).options(joinedload(BudgetModel.lines)).all()
        return [self._to_entity(m) for m in models]

    def delete(self, budget_id: str) -> bool:
        model = self.session.query(BudgetModel).filter_by(id=budget_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
