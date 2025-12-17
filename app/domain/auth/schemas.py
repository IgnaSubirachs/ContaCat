from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.domain.auth.entities import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str
    role: UserRole = UserRole.USER

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class PasswordChangeRequest(BaseModel):
    """Request schema for password change."""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validate password meets strength requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserSessionResponse(BaseModel):
    """Response schema for user session."""
    id: str
    user_id: int
    ip_address: str
    user_agent: str
    device_info: Optional[str]
    created_at: datetime
    last_activity: datetime
    is_active: bool
    is_current: bool = False  # Will be set by API to indicate current session

    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    """Extended user profile with sessions and activity."""
    id: int
    username: str
    role: str
    is_active: bool
    created_at: Optional[datetime]
    last_password_change: Optional[datetime]
    password_expires_in_days: Optional[int]
    active_sessions_count: int
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class LoginAttemptResponse(BaseModel):
    """Response schema for login attempts."""
    id: int
    username: str
    ip_address: str
    success: bool
    attempted_at: datetime
    failure_reason: Optional[str]

    class Config:
        from_attributes = True

class SecurityAlertResponse(BaseModel):
    """Response schema for security alerts."""
    alert_type: str  # "failed_logins", "locked_account", "password_expiry"
    user_id: Optional[int]
    username: str
    message: str
    severity: str  # "low", "medium", "high"
    timestamp: datetime

class ActivityStatsResponse(BaseModel):
    """Response schema for activity statistics."""
    total_users: int
    active_users: int
    inactive_users: int
    locked_users: int
    recent_logins_24h: int
    failed_logins_24h: int
    password_expiring_soon: int  # Within 7 days

class ForgotPasswordRequest(BaseModel):
    """Request schema for forgot password."""
    email: str = Field(..., max_length=255)

class ResetPasswordRequest(BaseModel):
    """Request schema for password reset."""
    token: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validate password meets strength requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v
