from sqlalchemy import Column, String, Integer, Float, Date, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.infrastructure.db.base import Base
from app.domain.banking.entities import StatementStatus

class BankStatementModel(Base):
    __tablename__ = "bank_statements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), nullable=False) # Helper link to internal account
    filename = Column(String(255), nullable=False)
    upload_date = Column(DateTime, default=datetime.now)
    status = Column(Enum(StatementStatus), default=StatementStatus.PENDING)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    lines = relationship("BankStatementLineModel", back_populates="statement", cascade="all, delete-orphan")

class BankStatementLineModel(Base):
    __tablename__ = "bank_statement_lines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    statement_id = Column(String(36), ForeignKey("bank_statements.id"), nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    concept = Column(String(255), nullable=True)
    balance = Column(Float, nullable=True)
    
    reconciled_entry_id = Column(String(36), nullable=True)
    status = Column(String(20), default="PENDING")

    # Relationships
    statement = relationship("BankStatementModel", back_populates="lines")
