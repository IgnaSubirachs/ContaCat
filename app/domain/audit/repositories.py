from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.audit.entities import AuditLog


class AuditRepository(ABC):
    """Abstract repository for audit logs."""
    
    @abstractmethod
    def add(self, audit_log: AuditLog) -> None:
        """Add a new audit log entry."""
        pass
    
    @abstractmethod
    def find_by_entity(self, entity_type: str, entity_id: str) -> List[AuditLog]:
        """Find all audit logs for a specific entity."""
        pass
    
    @abstractmethod
    def find_by_user(self, user: str) -> List[AuditLog]:
        """Find all audit logs by a specific user."""
        pass
    
    @abstractmethod
    def list_recent(self, limit: int = 100) -> List[AuditLog]:
        """List recent audit logs."""
        pass
