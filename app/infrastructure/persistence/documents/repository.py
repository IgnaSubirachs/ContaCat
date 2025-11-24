from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.documents.entities import Document
from app.domain.documents.repositories import DocumentRepository
from app.infrastructure.persistence.documents.models import DocumentModel
from app.infrastructure.db.base import SessionLocal


class SqlAlchemyDocumentRepository(DocumentRepository):
    """SQLAlchemy-based implementation of DocumentRepository."""

    def __init__(self, session_factory=SessionLocal):
        self._session_factory = session_factory

    def add(self, document: Document) -> None:
        session: Session = self._session_factory()
        try:
            model = DocumentModel(
                id=document.id,
                entity_type=document.entity_type,
                entity_id=document.entity_id,
                filename=document.filename,
                file_path=document.file_path,
                file_type=document.file_type,
                document_type=document.document_type,
                file_size=document.file_size,
                uploaded_by=document.uploaded_by,
                uploaded_at=document.uploaded_at
            )
            session.add(model)
            session.commit()
        finally:
            session.close()

    def find_by_id(self, document_id: str) -> Optional[Document]:
        session: Session = self._session_factory()
        try:
            stmt = select(DocumentModel).where(DocumentModel.id == document_id)
            result = session.execute(stmt)
            model: DocumentModel | None = result.scalars().first()
            if not model:
                return None
            return self._model_to_entity(model)
        finally:
            session.close()

    def find_by_entity(self, entity_type: str, entity_id: str) -> List[Document]:
        session: Session = self._session_factory()
        try:
            stmt = select(DocumentModel).where(
                DocumentModel.entity_type == entity_type,
                DocumentModel.entity_id == entity_id
            ).order_by(DocumentModel.uploaded_at.desc())
            result = session.execute(stmt)
            models: List[DocumentModel] = result.scalars().all()
            return [self._model_to_entity(m) for m in models]
        finally:
            session.close()

    def delete(self, document_id: str) -> None:
        session: Session = self._session_factory()
        try:
            stmt = select(DocumentModel).where(DocumentModel.id == document_id)
            result = session.execute(stmt)
            model: DocumentModel | None = result.scalars().first()
            
            if not model:
                raise ValueError(f"No s'ha trobat el document amb ID {document_id}")
            
            session.delete(model)
            session.commit()
        finally:
            session.close()

    def _model_to_entity(self, model: DocumentModel) -> Document:
        """Convert SQLAlchemy model to domain entity."""
        return Document(
            id=model.id,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            filename=model.filename,
            file_path=model.file_path,
            file_type=model.file_type,
            document_type=model.document_type,
            file_size=model.file_size,
            uploaded_by=model.uploaded_by,
            uploaded_at=model.uploaded_at
        )
