from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.finance.entities import Loan

class LoanRepository(ABC):
    @abstractmethod
    def save(self, loan: Loan) -> Loan:
        pass

    @abstractmethod
    def find_by_id(self, loan_id: str) -> Optional[Loan]:
        pass

    @abstractmethod
    def list_all(self) -> List[Loan]:
        pass
        
    @abstractmethod
    def delete(self, loan_id: str) -> bool:
        pass
