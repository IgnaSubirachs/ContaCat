from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.partners.entities import Partner


class PartnerRepository(ABC):
    """Abstract repository for Partner entities."""
    
    @abstractmethod
    def add(self, partner: Partner) -> None:
        """Add a new partner."""
        pass
    
    @abstractmethod
    def list_all(self) -> List[Partner]:
        """List all partners."""
        pass
    
    @abstractmethod
    def find_by_id(self, partner_id: str) -> Optional[Partner]:
        """Find a partner by ID."""
        pass
    
    @abstractmethod
    def find_by_tax_id(self, tax_id: str) -> Optional[Partner]:
        """Find a partner by tax ID."""
        pass
