from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid
import json


@dataclass
class AuditLog:
    """Audit log entity for tracking changes."""
    entity_type: str  # "PARTNER", "EMPLOYEE", etc.
    entity_id: str  # ID of the entity
    action: str  # "CREATE", "UPDATE", "DELETE"
    user: str  # Who made the change
    changes: str  # JSON with old/new values
    timestamp: datetime
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
    
    @staticmethod
    def create_log(
        entity_type: str,
        entity_id: str,
        action: str,
        user: str = "system",
        old_values: dict = None,
        new_values: dict = None
    ) -> "AuditLog":
        """Create an audit log entry."""
        changes = {
            "old": old_values or {},
            "new": new_values or {}
        }
        
        return AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user=user,
            changes=json.dumps(changes, default=str),
            timestamp=datetime.now()
        )
    
    def get_changes_dict(self) -> dict:
        """Parse changes JSON to dict."""
        try:
            return json.loads(self.changes)
        except:
            return {"old": {}, "new": {}}
    
    def get_changed_fields(self) -> list:
        """Get list of fields that changed."""
        changes_dict = self.get_changes_dict()
        old_vals = changes_dict.get("old", {})
        new_vals = changes_dict.get("new", {})
        
        changed = []
        for key in set(list(old_vals.keys()) + list(new_vals.keys())):
            if old_vals.get(key) != new_vals.get(key):
                changed.append(key)
        
        return changed
