from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.budgets.entities import Budget

class BudgetRepository(ABC):
    @abstractmethod
    def save(self, budget: Budget) -> Budget:
        pass

    @abstractmethod
    def find_by_id(self, budget_id: str) -> Optional[Budget]:
        pass

    @abstractmethod
    def list_all(self) -> List[Budget]:
        pass

    @abstractmethod
    def delete(self, budget_id: str) -> bool:
        pass
