from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SqlEnum, Text, ForeignKey
from sqlalchemy.sql import func
from app.infrastructure.db.base import Base
from app.domain.auth.entities import UserRole

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SqlEnum(UserRole), nullable=False, default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_password_change = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class UserSessionModel(Base):
    """Model for tracking user sessions."""
    __tablename__ = "user_sessions"
    
    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)  # IPv6 max length
    user_agent = Column(Text)
    device_info = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True, index=True)

class PasswordHistoryModel(Base):
    """Model for password history."""
    __tablename__ = "password_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class LoginAttemptModel(Base):
    """Model for login attempts tracking."""
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text)
    success = Column(Boolean, nullable=False, index=True)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    failure_reason = Column(String(255))

class PasswordResetTokenModel(Base):
    """Model for password reset tokens."""
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    used = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
