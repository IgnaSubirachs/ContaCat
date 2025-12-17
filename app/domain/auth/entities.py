from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import uuid

class UserRole(Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    USER = "USER"
    READ_ONLY = "READ_ONLY"

@dataclass
class User:
    username: str
    password_hash: str
    role: UserRole
    is_active: bool = True
    id: Optional[int] = None
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_password_change: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None

@dataclass
class UserSession:
    """User session tracking entity."""
    user_id: int
    token: str
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    is_active: bool = True
    id: Optional[str] = None
    device_info: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())

@dataclass
class PasswordHistory:
    """Password history for preventing reuse."""
    user_id: int
    password_hash: str
    created_at: datetime
    id: Optional[int] = None

@dataclass
class LoginAttempt:
    """Login attempt tracking for security."""
    username: str
    ip_address: str
    user_agent: str
    success: bool
    attempted_at: datetime
    failure_reason: Optional[str] = None
    id: Optional[int] = None

@dataclass
class PasswordResetToken:
    """Password reset token for email-based password recovery."""
    user_id: int
    token: str
    expires_at: datetime
    used: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None
