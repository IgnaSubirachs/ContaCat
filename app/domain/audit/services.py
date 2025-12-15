from typing import List, Optional, Dict
from app.domain.audit.entities import AuditLog
from app.domain.audit.repositories import AuditRepository

class AuditService:
    """Service for managing audit logs."""
    
    def __init__(self, audit_repo: AuditRepository):
        self._audit_repo = audit_repo
    
    def log_action(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        user: str = "system",
        old_values: Dict = None,
        new_values: Dict = None
    ) -> AuditLog:
        """
        Log a business action.
        """
        log = AuditLog.create_log(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user=user,
            old_values=old_values,
            new_values=new_values
        )
        self._audit_repo.add(log)
        return log
    
    def get_entity_history(self, entity_type: str, entity_id: str) -> List[AuditLog]:
        """Get history for an entity."""
        return self._audit_repo.find_by_entity(entity_type, entity_id)

    def get_user_activity(self, user: str) -> List[AuditLog]:
        """Get activity for a user."""
        return self._audit_repo.find_by_user(user)
