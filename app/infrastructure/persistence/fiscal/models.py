from sqlalchemy import Column, Integer, String, Date, DateTime, Enum
from sqlalchemy.sql import func
from app.infrastructure.db.base import Base
from app.domain.fiscal.entities import FiscalYearStatus
import enum


class FiscalYearStatusDB(enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class FiscalYearModel(Base):
    """SQLAlchemy model for fiscal years."""
    __tablename__ = 'fiscal_years'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(Enum(FiscalYearStatusDB), nullable=False, default=FiscalYearStatusDB.OPEN)
    created_at = Column(DateTime, default=func.now())
