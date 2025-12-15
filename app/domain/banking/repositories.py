from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.banking.entities import BankStatement

class BankStatementRepository(ABC):
    @abstractmethod
    def save(self, statement: BankStatement) -> BankStatement:
        pass

    @abstractmethod
    def find_by_id(self, statement_id: str) -> Optional[BankStatement]:
        pass

    @abstractmethod
    def list_all(self) -> List[BankStatement]:
        pass

    @abstractmethod
    def delete(self, statement_id: str) -> bool:
        pass
