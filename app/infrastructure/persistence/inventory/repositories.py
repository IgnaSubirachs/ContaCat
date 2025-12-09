from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domain.inventory.entities import StockItem, StockMovement
from app.domain.inventory.repositories import StockItemRepository, StockMovementRepository
from app.infrastructure.persistence.inventory.models import StockItemModel, StockMovementModel
from app.infrastructure.db.base import SessionLocal


class SqlAlchemyStockItemRepository(StockItemRepository):
    """SQLAlchemy implementation of StockItemRepository."""
    
    def __init__(self, session_factory=SessionLocal):
        self._session_factory = session_factory
    
    def _to_entity(self, model: StockItemModel) -> StockItem:
        if not model:
            return None
        return StockItem(
            id=model.id,
            code=model.code,
            name=model.name,
            description=model.description,
            unit_price=model.unit_price,
            quantity=model.quantity,
            location=model.location,
            is_active=model.is_active
        )
    
    def save(self, item: StockItem) -> StockItem:
        session: Session = self._session_factory()
        try:
            existing = session.query(StockItemModel).filter(StockItemModel.id == item.id).first()
            if existing:
                existing.code = item.code
                existing.name = item.name
                existing.description = item.description
                existing.unit_price = item.unit_price
                existing.quantity = item.quantity
                existing.location = item.location
                existing.is_active = item.is_active
            else:
                model = StockItemModel(
                    id=item.id,
                    code=item.code,
                    name=item.name,
                    description=item.description,
                    unit_price=item.unit_price,
                    quantity=item.quantity,
                    location=item.location,
                    is_active=item.is_active
                )
                session.add(model)
            session.commit()
            return item
        finally:
            session.close()
    
    def find_by_id(self, item_id: str) -> Optional[StockItem]:
        session: Session = self._session_factory()
        try:
            model = session.query(StockItemModel).filter(StockItemModel.id == item_id).first()
            return self._to_entity(model)
        finally:
            session.close()
    
    def find_by_code(self, code: str) -> Optional[StockItem]:
        session: Session = self._session_factory()
        try:
            model = session.query(StockItemModel).filter(StockItemModel.code == code).first()
            return self._to_entity(model)
        finally:
            session.close()
    
    def list_all(self) -> List[StockItem]:
        session: Session = self._session_factory()
        try:
            models = session.query(StockItemModel).filter(StockItemModel.is_active == True).all()
            return [self._to_entity(m) for m in models]
        finally:
            session.close()
    
    def delete(self, item_id: str) -> None:
        session: Session = self._session_factory()
        try:
            model = session.query(StockItemModel).filter(StockItemModel.id == item_id).first()
            if model:
                session.delete(model)
                session.commit()
        finally:
            session.close()


class SqlAlchemyStockMovementRepository(StockMovementRepository):
    """SQLAlchemy implementation of StockMovementRepository."""
    
    def __init__(self, session_factory=SessionLocal):
        self._session_factory = session_factory
    
    def _to_entity(self, model: StockMovementModel) -> StockMovement:
        if not model:
            return None
        return StockMovement(
            id=model.id,
            stock_item_code=model.stock_item_code,
            date=model.date,
            quantity=model.quantity,
            description=model.description
        )
    
    def save(self, movement: StockMovement) -> StockMovement:
        session: Session = self._session_factory()
        try:
            model = StockMovementModel(
                id=movement.id,
                stock_item_code=movement.stock_item_code,
                date=movement.date,
                quantity=movement.quantity,
                description=movement.description
            )
            session.add(model)
            session.commit()
            return movement
        finally:
            session.close()
    
    def find_by_id(self, movement_id: str) -> Optional[StockMovement]:
        session: Session = self._session_factory()
        try:
            model = session.query(StockMovementModel).filter(StockMovementModel.id == movement_id).first()
            return self._to_entity(model)
        finally:
            session.close()
    
    def list_by_item_code(self, item_code: str) -> List[StockMovement]:
        session: Session = self._session_factory()
        try:
            models = session.query(StockMovementModel).filter(
                StockMovementModel.stock_item_code == item_code
            ).order_by(StockMovementModel.date.desc()).all()
            return [self._to_entity(m) for m in models]
        finally:
            session.close()
    
    def list_all(self) -> List[StockMovement]:
        session: Session = self._session_factory()
        try:
            models = session.query(StockMovementModel).order_by(StockMovementModel.date.desc()).all()
            return [self._to_entity(m) for m in models]
        finally:
            session.close()
