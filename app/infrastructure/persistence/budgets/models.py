from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.infrastructure.db.base import Base
from app.domain.budgets.entities import BudgetStatus

class BudgetModel(Base):
    __tablename__ = "budgets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    year = Column(Integer, nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(Enum(BudgetStatus), default=BudgetStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    lines = relationship("BudgetLineModel", back_populates="budget", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "year": self.year,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "lines": [line.to_dict() for line in self.lines]
        }

class BudgetLineModel(Base):
    __tablename__ = "budget_lines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    budget_id = Column(String(36), ForeignKey("budgets.id"), nullable=False)
    account_group = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)

    # Relationships
    budget = relationship("BudgetModel", back_populates="lines")

    def to_dict(self):
        return {
            "id": self.id,
            "budget_id": self.budget_id,
            "account_group": self.account_group,
            "amount": self.amount
        }
