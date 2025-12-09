from sqlalchemy import Column, String, Float, Integer, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base


class StockItemModel(Base):
    __tablename__ = "stock_items"
    
    id = Column(String(36), primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    unit_price = Column(Float, default=0.0)
    quantity = Column(Integer, default=0)
    location = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    
    movements = relationship("StockMovementModel", back_populates="stock_item", cascade="all, delete-orphan")


class StockMovementModel(Base):
    __tablename__ = "stock_movements"
    
    id = Column(String(36), primary_key=True, index=True)
    stock_item_code = Column(String(50), ForeignKey("stock_items.code"), nullable=False)
    date = Column(Date, nullable=False)
    quantity = Column(Integer, nullable=False)
    description = Column(String(255), nullable=True)
    
    stock_item = relationship("StockItemModel", back_populates="movements")
