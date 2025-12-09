from typing import List, Optional
from app.domain.inventory.entities import StockItem, StockMovement
from app.domain.inventory.repositories import StockItemRepository, StockMovementRepository


class InventoryService:
    """Service for inventory operations."""
    
    def __init__(
        self,
        stock_item_repo: StockItemRepository,
        stock_movement_repo: StockMovementRepository
    ):
        self._item_repo = stock_item_repo
        self._movement_repo = stock_movement_repo
    
    # Stock Item operations
    def create_item(self, item: StockItem) -> StockItem:
        """Create a new stock item."""
        item.validate()
        
        existing = self._item_repo.find_by_code(item.code)
        if existing:
            raise ValueError(f"Ja existeix un article amb el codi {item.code}")
        
        return self._item_repo.save(item)
    
    def update_item(self, item: StockItem) -> StockItem:
        """Update an existing stock item."""
        item.validate()
        
        existing = self._item_repo.find_by_id(item.id)
        if not existing:
            raise ValueError(f"No s'ha trobat l'article amb ID {item.id}")
        
        return self._item_repo.save(item)
    
    def get_item(self, item_id: str) -> Optional[StockItem]:
        """Get a stock item by ID."""
        return self._item_repo.find_by_id(item_id)
    
    def get_item_by_code(self, code: str) -> Optional[StockItem]:
        """Get a stock item by code."""
        return self._item_repo.find_by_code(code)
    
    def list_items(self) -> List[StockItem]:
        """List all stock items."""
        return self._item_repo.list_all()
    
    def delete_item(self, item_id: str) -> None:
        """Delete a stock item."""
        existing = self._item_repo.find_by_id(item_id)
        if not existing:
            raise ValueError(f"No s'ha trobat l'article amb ID {item_id}")
        
        self._item_repo.delete(item_id)
    
    # Stock Movement operations
    def register_movement(self, movement: StockMovement) -> StockMovement:
        """Register a stock movement (entrada o sortida)."""
        movement.validate()
        
        # Verify item exists
        item = self._item_repo.find_by_code(movement.stock_item_code)
        if not item:
            raise ValueError(f"No s'ha trobat l'article amb codi {movement.stock_item_code}")
        
        # Update item quantity
        new_quantity = item.quantity + movement.quantity
        if new_quantity < 0:
            raise ValueError(f"Stock insuficient. Disponible: {item.quantity}, Sol·licitat: {abs(movement.quantity)}")
        
        item.quantity = new_quantity
        self._item_repo.save(item)
        
        return self._movement_repo.save(movement)
    
    def list_movements(self, item_code: Optional[str] = None) -> List[StockMovement]:
        """List movements, optionally filtered by item code."""
        if item_code:
            return self._movement_repo.list_by_item_code(item_code)
        return self._movement_repo.list_all()
    
    def get_stock_level(self, item_code: str) -> int:
        """Get current stock level for an item."""
        item = self._item_repo.find_by_code(item_code)
        if not item:
            raise ValueError(f"No s'ha trobat l'article amb codi {item_code}")
        return item.quantity
