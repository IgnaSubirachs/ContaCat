from sqlalchemy import Column, String, Integer, Float, Date, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.infrastructure.db.base import Base
from app.domain.finance.entities import LoanStatus, AmortizationStatus

class LoanModel(Base):
    __tablename__ = "loans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    lender_partner_id = Column(String(36), nullable=False) # FK to partners not strictly enforced in DB for decoupling, or could be
    principal_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    duration_months = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(LoanStatus), default=LoanStatus.ACTIVE)
    
    # Financial Accounts Configuration
    account_principal_long_term = Column(String(20), nullable=False)
    account_principal_short_term = Column(String(20), nullable=False)
    account_interest_expense = Column(String(20), nullable=False)
    account_bank = Column(String(20), nullable=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    amortization_schedule = relationship("AmortizationEntryModel", back_populates="loan", cascade="all, delete-orphan", order_by="AmortizationEntryModel.installment_number")

class AmortizationEntryModel(Base):
    __tablename__ = "loan_amortization_schedule"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    loan_id = Column(String(36), ForeignKey("loans.id"), nullable=False)
    installment_number = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False)
    
    principal_payment = Column(Float, nullable=False)
    interest_payment = Column(Float, nullable=False)
    total_payment = Column(Float, nullable=False)
    remaining_balance = Column(Float, nullable=False)
    
    status = Column(Enum(AmortizationStatus), default=AmortizationStatus.PENDING)
    journal_entry_id = Column(String(36), nullable=True) # ID of the generated accounting entry

    # Relationships
    loan = relationship("LoanModel", back_populates="amortization_schedule")
