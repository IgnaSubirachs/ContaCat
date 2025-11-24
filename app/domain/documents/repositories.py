from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.documents.entities import Document


class DocumentRepository(ABC):
    """Abstract repository for documents."""
    
    @abstractmethod
    def add(self, document: Document) -> None:
        """Add a new document."""
        pass
    
    @abstractmethod
    def find_by_id(self, document_id: str) -> Optional[Document]:
        """Find a document by ID."""
        pass
    
    @abstractmethod
    def find_by_entity(self, entity_type: str, entity_id: str) -> List[Document]:
        """Find all documents for a specific entity."""
        pass
    
    @abstractmethod
    def delete(self, document_id: str) -> None:
        """Delete a document."""
        pass
