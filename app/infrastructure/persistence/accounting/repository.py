from typing import List, Optional
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.domain.accounting.entities import (
    JournalEntry, JournalLine, JournalEntryStatus
)
from app.domain.accounting.repositories import JournalRepository
from app.infrastructure.persistence.accounting.models import (
    JournalEntryModel, JournalLineModel
)
from app.infrastructure.db.base import SessionLocal


class SqlAlchemyJournalRepository(JournalRepository):
    """SQLAlchemy implementation of JournalRepository."""

    def __init__(self, session_factory=SessionLocal):
        self._session_factory = session_factory

    def add(self, entry: JournalEntry) -> None:
        session: Session = self._session_factory()
        try:
            # Create entry model
            entry_model = JournalEntryModel(
                id=entry.id,
                entry_number=entry.entry_number,
                entry_date=entry.entry_date,
                description=entry.description,
                status=entry.status,
                attachment_path=entry.attachment_path
            )
            
            # Create line models
            for line in entry.lines:
                line_model = JournalLineModel(
                    id=line.id,
                    journal_entry_id=entry.id,
                    account_code=line.account_code,
                    debit=line.debit,
                    credit=line.credit,
                    description=line.description
                )
                entry_model.lines.append(line_model)
            
            session.add(entry_model)
            session.commit()
        finally:
            session.close()

    def find_by_id(self, entry_id: str) -> Optional[JournalEntry]:
        session: Session = self._session_factory()
        try:
            stmt = select(JournalEntryModel).options(
                joinedload(JournalEntryModel.lines)
            ).where(JournalEntryModel.id == entry_id)
            result = session.execute(stmt)
            model: JournalEntryModel | None = result.scalars().first()
            if not model:
                return None
            return self._model_to_entity(model)
        finally:
            session.close()

    def find_by_number(self, entry_number: int) -> Optional[JournalEntry]:
        session: Session = self._session_factory()
        try:
            stmt = select(JournalEntryModel).options(
                joinedload(JournalEntryModel.lines)
            ).where(JournalEntryModel.entry_number == entry_number)
            result = session.execute(stmt)
            model: JournalEntryModel | None = result.scalars().first()
            if not model:
                return None
            return self._model_to_entity(model)
        finally:
            session.close()

    def list_all(self) -> List[JournalEntry]:
        session: Session = self._session_factory()
        try:
            stmt = select(JournalEntryModel).options(
                joinedload(JournalEntryModel.lines)
            ).order_by(JournalEntryModel.entry_number.desc())
            result = session.execute(stmt)
            models: List[JournalEntryModel] = result.scalars().unique().all()
            return [self._model_to_entity(m) for m in models]
        finally:
            session.close()

    def list_by_date_range(self, start_date: date, end_date: date) -> List[JournalEntry]:
        session: Session = self._session_factory()
        try:
            stmt = select(JournalEntryModel).options(
                joinedload(JournalEntryModel.lines)
            ).where(
                JournalEntryModel.entry_date >= start_date,
                JournalEntryModel.entry_date <= end_date
            ).order_by(JournalEntryModel.entry_date, JournalEntryModel.entry_number)
            result = session.execute(stmt)
            models: List[JournalEntryModel] = result.scalars().unique().all()
            return [self._model_to_entity(m) for m in models]
        finally:
            session.close()

    def get_next_entry_number(self) -> int:
        session: Session = self._session_factory()
        try:
            stmt = select(func.max(JournalEntryModel.entry_number))
            result = session.execute(stmt)
            max_number = result.scalar()
            return (max_number or 0) + 1
        finally:
            session.close()

    def update(self, entry: JournalEntry) -> None:
        session: Session = self._session_factory()
        try:
            stmt = select(JournalEntryModel).where(JournalEntryModel.id == entry.id)
            result = session.execute(stmt)
            model: JournalEntryModel | None = result.scalars().first()
            
            if not model:
                raise ValueError(f"No s'ha trobat l'assentament amb ID {entry.id}")
            
            model.description = entry.description
            model.status = entry.status
            
            session.commit()
        finally:
            session.close()

    def delete(self, entry_id: str) -> None:
        session: Session = self._session_factory()
        try:
            stmt = select(JournalEntryModel).where(JournalEntryModel.id == entry_id)
            result = session.execute(stmt)
            model: JournalEntryModel | None = result.scalars().first()
            
            if not model:
                raise ValueError(f"No s'ha trobat l'assentament amb ID {entry_id}")
            
            if model.status == JournalEntryStatus.POSTED:
                raise ValueError("No es pot eliminar un assentament comptabilitzat")
            
            session.delete(model)
            session.commit()
        finally:
            session.close()

    def _model_to_entity(self, model: JournalEntryModel) -> JournalEntry:
        """Convert model to entity."""
        lines = [
            JournalLine(
                id=line.id,
                account_code=line.account_code,
                debit=line.debit,
                credit=line.credit,
                description=line.description
            )
            for line in model.lines
        ]
        
        return JournalEntry(
            id=model.id,
            entry_number=model.entry_number,
            entry_date=model.entry_date,
            description=model.description,
            lines=lines,
            status=JournalEntryStatus(model.status),
            attachment_path=model.attachment_path
        )
