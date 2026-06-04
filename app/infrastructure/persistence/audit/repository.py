from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.audit.entities import AuditLog
from app.domain.audit.repositories import AuditRepository
from app.infrastructure.persistence.audit.models import AuditLogModel
from app.infrastructure.db.base import SessionLocal


class SqlAlchemyAuditRepository(AuditRepository):
    """SQLAlchemy-based implementation of AuditRepository."""

    def __init__(self, session_factory=SessionLocal):
        if isinstance(session_factory, Session):
            self._session = session_factory
            self._session_factory = None
        else:
            self._session = None
            self._session_factory = session_factory

    def _get_session(self) -> tuple[Session, bool]:
        if self._session is not None:
            return self._session, False
        return self._session_factory(), True

    def add(self, audit_log: AuditLog) -> None:
        session, should_close = self._get_session()
        try:
            model = AuditLogModel(
                id=audit_log.id,
                entity_type=audit_log.entity_type,
                entity_id=audit_log.entity_id,
                action=audit_log.action,
                user=audit_log.user,
                changes=audit_log.changes,
                timestamp=audit_log.timestamp
            )
            session.add(model)
            session.commit()
        finally:
            if should_close:
                session.close()

    def find_by_entity(self, entity_type: str, entity_id: str) -> List[AuditLog]:
        session, should_close = self._get_session()
        try:
            stmt = select(AuditLogModel).where(
                AuditLogModel.entity_type == entity_type,
                AuditLogModel.entity_id == entity_id
            ).order_by(AuditLogModel.timestamp.desc())
            result = session.execute(stmt)
            models: List[AuditLogModel] = result.scalars().all()
            return [self._model_to_entity(m) for m in models]
        finally:
            if should_close:
                session.close()

    def find_by_user(self, user: str) -> List[AuditLog]:
        session, should_close = self._get_session()
        try:
            stmt = select(AuditLogModel).where(
                AuditLogModel.user == user
            ).order_by(AuditLogModel.timestamp.desc())
            result = session.execute(stmt)
            models: List[AuditLogModel] = result.scalars().all()
            return [self._model_to_entity(m) for m in models]
        finally:
            if should_close:
                session.close()

    def list_recent(self, limit: int = 100) -> List[AuditLog]:
        session, should_close = self._get_session()
        try:
            stmt = select(AuditLogModel).order_by(
                AuditLogModel.timestamp.desc()
            ).limit(limit)
            result = session.execute(stmt)
            models: List[AuditLogModel] = result.scalars().all()
            return [self._model_to_entity(m) for m in models]
        finally:
            if should_close:
                session.close()

    def _model_to_entity(self, model: AuditLogModel) -> AuditLog:
        """Convert SQLAlchemy model to domain entity."""
        return AuditLog(
            id=model.id,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            action=model.action,
            user=model.user,
            changes=model.changes,
            timestamp=model.timestamp
        )
