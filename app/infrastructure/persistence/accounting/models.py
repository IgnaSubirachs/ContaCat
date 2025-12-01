from sqlalchemy import String, Integer, Boolean, Numeric, Date, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from decimal import Decimal
from typing import List

from app.infrastructure.db.base import Base
from app.domain.accounting.entities import JournalEntryStatus
from app.infrastructure.persistence.accounts.models import AccountModel


class JournalEntryModel(Base):
    """SQLAlchemy model for journal_entries table."""
    __tablename__ = "journal_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    entry_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(SQLEnum(JournalEntryStatus), nullable=False, default=JournalEntryStatus.DRAFT)

    # Relationship to lines
    lines: Mapped[List["JournalLineModel"]] = relationship(
        "JournalLineModel",
        back_populates="journal_entry",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<JournalEntryModel #{self.entry_number} - {self.entry_date}>"


class JournalLineModel(Base):
    """SQLAlchemy model for journal_lines table."""
    __tablename__ = "journal_lines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    journal_entry_id: Mapped[str] = mapped_column(String(36), ForeignKey("journal_entries.id"), nullable=False, index=True)
    account_code: Mapped[str] = mapped_column(String(20), ForeignKey("accounts.code"), nullable=False, index=True)
    debit: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    credit: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    description: Mapped[str] = mapped_column(String(500), default="")

    # Relationship to journal entry
    journal_entry: Mapped["JournalEntryModel"] = relationship(
        "JournalEntryModel",
        back_populates="lines"
    )

    def __repr__(self) -> str:
        return f"<JournalLineModel {self.account_code} D:{self.debit} C:{self.credit}>"
