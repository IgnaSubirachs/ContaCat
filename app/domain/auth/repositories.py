from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from .entities import User, UserSession, PasswordHistory, LoginAttempt

class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        pass

    @abstractmethod
    def list_all(self) -> List[User]:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass

class UserSessionRepository(ABC):
    """Repository for managing user sessions."""
    
    @abstractmethod
    def save(self, session: UserSession) -> UserSession:
        pass
    
    @abstractmethod
    def get_by_id(self, session_id: str) -> Optional[UserSession]:
        pass
    
    @abstractmethod
    def get_active_sessions(self, user_id: int) -> List[UserSession]:
        pass
    
    @abstractmethod
    def revoke_session(self, session_id: str) -> bool:
        pass
    
    @abstractmethod
    def update_last_activity(self, session_id: str) -> bool:
        pass
    
    @abstractmethod
    def cleanup_expired_sessions(self, hours: int) -> int:
        """Remove sessions older than specified hours."""
        pass

class PasswordHistoryRepository(ABC):
    """Repository for password history."""
    
    @abstractmethod
    def save(self, password_history: PasswordHistory) -> PasswordHistory:
        pass
    
    @abstractmethod
    def get_recent_passwords(self, user_id: int, count: int) -> List[PasswordHistory]:
        """Get the most recent N password hashes for a user."""
        pass

class LoginAttemptRepository(ABC):
    """Repository for login attempts."""
    
    @abstractmethod
    def save(self, attempt: LoginAttempt) -> LoginAttempt:
        pass
    
    @abstractmethod
    def get_recent_attempts(self, username: str, minutes: int) -> List[LoginAttempt]:
        """Get login attempts for a username within the last N minutes."""
        pass
    
    @abstractmethod
    def get_failed_attempts_count(self, username: str, minutes: int) -> int:
        """Count failed login attempts within the last N minutes."""
        pass
    
    @abstractmethod
    def get_recent_activity(self, limit: int = 100) -> List[LoginAttempt]:
        """Get recent login attempts for monitoring."""
        pass

class PasswordResetTokenRepository(ABC):
    """Repository for password reset tokens."""
    
    @abstractmethod
    def create(self, token: 'PasswordResetToken') -> 'PasswordResetToken':
        """Create a password reset token."""
        pass
    
    @abstractmethod
    def get_by_token(self, token_str: str) -> Optional['PasswordResetToken']:
        """Get a password reset token by token string."""
        pass
    
    @abstractmethod
    def mark_as_used(self, token_id: int) -> None:
        """Mark a token as used."""
        pass
    
    @abstractmethod
    def cleanup_expired(self) -> int:
        """Cleanup expired tokens. Returns count of deleted tokens."""
        pass
    
    @abstractmethod
    def count_recent_requests(self, user_id: int, minutes: int) -> int:
        """Count recent reset requests for rate limiting."""
        pass
