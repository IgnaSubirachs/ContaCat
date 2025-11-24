# Domain entities for Inventory module

from dataclasses import dataclass
from datetime import date
from typing import Optional
import uuid


@dataclass
class StockItem:
    """Representa un article d'inventari.
    
    - `code`: Codi únic de l'article (ex: SKU).
    - `name`: Nom descriptiu.
    - `description`: Descripció opcional.
    - `unit_price`: Preu unitari.
    - `quantity`: Quantitat disponible.
    - `location`: Ubicació física (ex: "Warehouse A").
    - `is_active`: Indicador d'activitat.
    """
    code: str
    name: str
    description: Optional[str] = None
    unit_price: float = 0.0
    quantity: int = 0
    location: Optional[str] = None
    is_active: bool = True
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())

    def validate(self) -> None:
        if not self.code or not self.code.strip():
            raise ValueError("El codi de l'article és obligatori")
        if not self.name or not self.name.strip():
            raise ValueError("El nom de l'article és obligatori")
        if self.unit_price < 0:
            raise ValueError("El preu unitari no pot ser negatiu")
        if self.quantity < 0:
            raise ValueError("La quantitat no pot ser negativa")


@dataclass
class StockMovement:
    """Representa un moviment d'inventari (entrada o sortida).
    
    - `stock_item_code`: Codi de l'article al qual afecta.
    - `date`: Data del moviment.
    - `quantity`: Quantitat (positiva per entrada, negativa per sortida).
    - `description`: Motiu del moviment.
    """
    stock_item_code: str
    date: date
    quantity: int
    description: Optional[str] = None
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())

    def validate(self) -> None:
        if not self.stock_item_code or not self.stock_item_code.strip():
            raise ValueError("El codi de l'article és obligatori")
        if self.quantity == 0:
            raise ValueError("La quantitat ha de ser diferent de zero")
        # La data es valida implícitament per ser un objecte date
