import uuid
from typing import List, Optional
from datetime import datetime

from app.domain.budgets.entities import Budget, BudgetStatus, BudgetLine
from app.domain.budgets.repositories import BudgetRepository

class BudgetService:
    def __init__(self, repository: BudgetRepository):
        self.repository = repository

    def create_budget(self, name: str, year: int, description: str = None) -> Budget:
        budget = Budget(
            id=str(uuid.uuid4()),
            name=name,
            year=year,
            description=description,
            status=BudgetStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        return self.repository.save(budget)

    def get_budget(self, budget_id: str) -> Optional[Budget]:
        return self.repository.find_by_id(budget_id)

    def list_budgets(self) -> List[Budget]:
        return self.repository.list_all()

    def add_budget_line(self, budget_id: str, account_group: str, amount: float) -> Optional[Budget]:
        budget = self.repository.find_by_id(budget_id)
        if not budget:
            return None
        
        # Check if line for this group already exists, modify it? Or just add new?
        # For simplicity, we create a new line ID
        line_id = str(uuid.uuid4())
        new_line = BudgetLine(
            id=line_id,
            budget_id=budget_id,
            account_group=account_group,
            amount=amount
        )
        budget.lines.append(new_line)
        budget.updated_at = datetime.now()
        return self.repository.save(budget)

    def update_status(self, budget_id: str, status: BudgetStatus) -> Optional[Budget]:
        budget = self.repository.find_by_id(budget_id)
        if not budget:
            return None
        budget.status = status
        budget.updated_at = datetime.now()
        return self.repository.save(budget)

    def delete_budget(self, budget_id: str) -> bool:
        return self.repository.delete(budget_id)
