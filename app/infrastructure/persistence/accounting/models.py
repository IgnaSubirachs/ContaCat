from sqlalchemy import String, Integer, Boolean, Numeric, Date, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from decimal import Decimal
from typing import List

from app.infrastructure.db.base import Base
from app.domain.accounting.entities import AccountType, JournalEntryStatus


class AccountModel(Base):
    """SQLAlchemy model for accounts table."""
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    account_type: Mapped[str] = mapped_column(SQLEnum(AccountType), nullable=False)
    group: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_code: Mapped[str] = mapped_column(String(20), nullable=True)

    def __repr__(self) -> str:
        return f"<AccountModel {self.code} - {self.name}>"


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
    journal_entry_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    account_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
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
