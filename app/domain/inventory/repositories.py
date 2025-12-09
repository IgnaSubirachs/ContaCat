from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.inventory.entities import StockItem, StockMovement


class StockItemRepository(ABC):
    """Repository interface for StockItem."""
    
    @abstractmethod
    def save(self, item: StockItem) -> StockItem:
        """Save a stock item."""
        pass
    
    @abstractmethod
    def find_by_id(self, item_id: str) -> Optional[StockItem]:
        """Find a stock item by ID."""
        pass
    
    @abstractmethod
    def find_by_code(self, code: str) -> Optional[StockItem]:
        """Find a stock item by code."""
        pass
    
    @abstractmethod
    def list_all(self) -> List[StockItem]:
        """List all stock items."""
        pass
    
    @abstractmethod
    def delete(self, item_id: str) -> None:
        """Delete a stock item."""
        pass


class StockMovementRepository(ABC):
    """Repository interface for StockMovement."""
    
    @abstractmethod
    def save(self, movement: StockMovement) -> StockMovement:
        """Save a stock movement."""
        pass
    
    @abstractmethod
    def find_by_id(self, movement_id: str) -> Optional[StockMovement]:
        """Find a movement by ID."""
        pass
    
    @abstractmethod
    def list_by_item_code(self, item_code: str) -> List[StockMovement]:
        """List all movements for a specific item."""
        pass
    
    @abstractmethod
    def list_all(self) -> List[StockMovement]:
        """List all movements."""
        pass
