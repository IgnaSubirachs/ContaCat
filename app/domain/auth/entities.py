from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

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
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
