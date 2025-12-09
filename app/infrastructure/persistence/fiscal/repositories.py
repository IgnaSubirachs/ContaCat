from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.domain.fiscal.entities import FiscalYear, FiscalYearStatus
from app.domain.fiscal.repositories import FiscalYearRepository
from app.infrastructure.persistence.fiscal.models import FiscalYearModel, FiscalYearStatusDB
from app.infrastructure.db.base import SessionLocal


class SqlAlchemyFiscalYearRepository(FiscalYearRepository):
    """SQLAlchemy implementation of FiscalYearRepository."""
    
    def __init__(self, session_factory=SessionLocal):
        self._session_factory = session_factory
    
    def _to_entity(self, model: FiscalYearModel) -> FiscalYear:
        """Convert SQLAlchemy model to domain entity."""
        return FiscalYear(
            id=model.id,
            name=model.name,
            start_date=model.start_date,
            end_date=model.end_date,
            status=FiscalYearStatus(model.status.value),
            created_at=model.created_at
        )
    
    def _to_model(self, entity: FiscalYear) -> FiscalYearModel:
        """Convert domain entity to SQLAlchemy model."""
        return FiscalYearModel(
            id=entity.id,
            name=entity.name,
            start_date=entity.start_date,
            end_date=entity.end_date,
            status=FiscalYearStatusDB(entity.status.value),
            created_at=entity.created_at
        )
    
    def add(self, fiscal_year: FiscalYear) -> FiscalYear:
        with self._session_factory() as session:
            model = FiscalYearModel(
                name=fiscal_year.name,
                start_date=fiscal_year.start_date,
                end_date=fiscal_year.end_date,
                status=FiscalYearStatusDB(fiscal_year.status.value)
            )
            session.add(model)
            session.commit()
            session.refresh(model)
            return self._to_entity(model)
    
    def get_by_id(self, fiscal_year_id: int) -> Optional[FiscalYear]:
        with self._session_factory() as session:
            model = session.query(FiscalYearModel).filter(
                FiscalYearModel.id == fiscal_year_id
            ).first()
            return self._to_entity(model) if model else None
    
    def get_by_name(self, name: str) -> Optional[FiscalYear]:
        with self._session_factory() as session:
            model = session.query(FiscalYearModel).filter(
                FiscalYearModel.name == name
            ).first()
            return self._to_entity(model) if model else None
    
    def get_current(self) -> Optional[FiscalYear]:
        with self._session_factory() as session:
            model = session.query(FiscalYearModel).filter(
                FiscalYearModel.status == FiscalYearStatusDB.OPEN
            ).order_by(FiscalYearModel.start_date.desc()).first()
            return self._to_entity(model) if model else None
    
    def get_by_date(self, check_date: date) -> Optional[FiscalYear]:
        with self._session_factory() as session:
            model = session.query(FiscalYearModel).filter(
                FiscalYearModel.start_date <= check_date,
                FiscalYearModel.end_date >= check_date
            ).first()
            return self._to_entity(model) if model else None
    
    def list_all(self) -> List[FiscalYear]:
        with self._session_factory() as session:
            models = session.query(FiscalYearModel).order_by(
                FiscalYearModel.start_date.desc()
            ).all()
            return [self._to_entity(m) for m in models]
    
    def update(self, fiscal_year: FiscalYear) -> FiscalYear:
        with self._session_factory() as session:
            model = session.query(FiscalYearModel).filter(
                FiscalYearModel.id == fiscal_year.id
            ).first()
            if model:
                model.name = fiscal_year.name
                model.start_date = fiscal_year.start_date
                model.end_date = fiscal_year.end_date
                model.status = FiscalYearStatusDB(fiscal_year.status.value)
                session.commit()
                session.refresh(model)
                return self._to_entity(model)
            return None
