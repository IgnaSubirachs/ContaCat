from datetime import datetime, timedelta
from typing import Optional, List
from passlib.context import CryptContext
from jose import JWTError, jwt
import re
from app.domain.auth.entities import User, UserSession, PasswordHistory, LoginAttempt
from app.domain.auth.repositories import (
    UserRepository, UserSessionRepository,
    PasswordHistoryRepository, LoginAttemptRepository
)

# Security configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # TODO: Move to .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password policies
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = True
PASSWORD_EXPIRY_DAYS = 30
PASSWORD_HISTORY_COUNT = 5  # No reutilitzar últimes 5 contrasenyes

# Account lockout
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

# Session management
SESSION_TIMEOUT_HOURS = 24  # Sessions caduquen després de 24h d'inactivitat

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

class AuthService:
    def __init__(
        self, 
        user_repository: UserRepository,
        session_repository: Optional[UserSessionRepository] = None,
        password_history_repository: Optional[PasswordHistoryRepository] = None,
        login_attempt_repository: Optional[LoginAttemptRepository] = None,
        audit_service=None
    ):
        self._user_repo = user_repository
        self._session_repo = session_repository
        self._password_history_repo = password_history_repository
        self._login_attempt_repo = login_attempt_repository
        self._audit = audit_service

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def validate_password_strength(self, password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password meets strength requirements.
        Returns (is_valid, error_message).
        """
        if len(password) < PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters"
        
        if PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if PASSWORD_REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if PASSWORD_REQUIRE_DIGIT and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        if PASSWORD_REQUIRE_SPECIAL:
            special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
            if not any(c in special_chars for c in password):
                return False, "Password must contain at least one special character"
        
        return True, None

    def check_password_in_history(self, user_id: int, password: str) -> bool:
        """Check if password was recently used."""
        if not self._password_history_repo:
            return False
        
        recent_passwords = self._password_history_repo.get_recent_passwords(
            user_id, PASSWORD_HISTORY_COUNT
        )
        
        for pwd_history in recent_passwords:
            if self.verify_password(password, pwd_history.password_hash):
                return True
        return False

    def check_password_expiry(self, user: User) -> tuple[bool, Optional[int]]:
        """
        Check if password has expired.
        Returns (is_expired, days_until_expiry).
        """
        if not user.last_password_change:
            return True, 0  # No password change date means expired
        
        days_since_change = (datetime.now() - user.last_password_change).days
        days_until_expiry = PASSWORD_EXPIRY_DAYS - days_since_change
        
        return days_until_expiry <= 0, days_until_expiry

    def check_account_lockout(self, username: str) -> tuple[bool, Optional[datetime]]:
        """
        Check if account is locked out.
        Returns (is_locked, locked_until).
        """
        user = self._user_repo.get_by_username(username)
        if not user:
            return False, None
        
        if user.locked_until and user.locked_until > datetime.now():
            return True, user.locked_until
        
        # Clear lockout if it has expired
        if user.locked_until and user.locked_until <= datetime.now():
            user.locked_until = None
            user.failed_login_attempts = 0
            self._user_repo.save(user)
        
        return False, None

    def record_login_attempt(
        self, 
        username: str, 
        ip_address: str,
        user_agent: str,
        success: bool,
        failure_reason: Optional[str] = None
    ):
        """Record a login attempt."""
        if not self._login_attempt_repo:
            return
        
        attempt = LoginAttempt(
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            attempted_at=datetime.now(),
            failure_reason=failure_reason
        )
        self._login_attempt_repo.save(attempt)
        
        # Update failed attempts counter
        if not success:
            user = self._user_repo.get_by_username(username)
            if user:
                user.failed_login_attempts += 1
                
                # Lock account if max attempts reached
                if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
                    user.locked_until = datetime.now() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                    if self._audit:
                        self._audit.log_action(
                            entity_type="USER",
                            entity_id=str(user.id),
                            action="ACCOUNT_LOCKED",
                            user="system",
                            details=f"Account locked after {MAX_LOGIN_ATTEMPTS} failed attempts"
                        )
                
                self._user_repo.save(user)
        else:
            # Reset failed attempts on successful login
            user = self._user_repo.get_by_username(username)
            if user and user.failed_login_attempts > 0:
                user.failed_login_attempts = 0
                user.locked_until = None
                self._user_repo.save(user)

    def create_session(
        self,
        user_id: int,
        token: str,
        ip_address: str,
        user_agent: str
    ) -> Optional[UserSession]:
        """Create a new user session."""
        if not self._session_repo:
            return None
        
        # Parse device info from user agent
        device_info = self._parse_device_info(user_agent)
        
        session = UserSession(
            user_id=user_id,
            token=token,
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=device_info,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        return self._session_repo.save(session)

    def _parse_device_info(self, user_agent: str) -> str:
        """Parse device information from user agent string."""
        # Simple device detection
        if 'Mobile' in user_agent:
            if 'iPhone' in user_agent:
                return 'iPhone'
            elif 'Android' in user_agent:
                return 'Android'
            return 'Mobile'
        elif 'Tablet' in user_agent or 'iPad' in user_agent:
            return 'Tablet'
        else:
            if 'Windows' in user_agent:
                return 'Windows PC'
            elif 'Mac' in user_agent:
                return 'Mac'
            elif 'Linux' in user_agent:
                return 'Linux'
            return 'Desktop'

    def get_active_sessions(self, user_id: int) -> List[UserSession]:
        """Get all active sessions for a user."""
        if not self._session_repo:
            return []
        return self._session_repo.get_active_sessions(user_id)

    def revoke_session(self, session_id: str) -> bool:
        """Revoke a specific session."""
        if not self._session_repo:
            return False
        return self._session_repo.revoke_session(session_id)

    def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str
    ) -> tuple[bool, Optional[str]]:
        """
        Change user password with validation.
        Returns (success, error_message).
        """
        # Verify current password
        if not self.verify_password(current_password, user.password_hash):
            return False, "Current password is incorrect"
        
        # Validate new password strength
        is_valid, error = self.validate_password_strength(new_password)
        if not is_valid:
            return False, error
        
        # Check password history
        if self.check_password_in_history(user.id, new_password):
            return False, f"Cannot reuse any of your last {PASSWORD_HISTORY_COUNT} passwords"
        
        # Save old password to history
        if self._password_history_repo:
            pwd_history = PasswordHistory(
                user_id=user.id,
                password_hash=user.password_hash,
                created_at=datetime.now()
            )
            self._password_history_repo.save(pwd_history)
        
        # Update password
        user.password_hash = self.get_password_hash(new_password)
        user.last_password_change = datetime.now()
        self._user_repo.save(user)
        
        # Log action
        if self._audit:
            self._audit.log_action(
                entity_type="USER",
                entity_id=str(user.id),
                action="PASSWORD_CHANGED",
                user=user.username,
                details="Password changed successfully"
            )
        
        return True, None

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password."""
        user = self._user_repo.get_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str) -> Optional[dict]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    def create_user(self, username: str, password: str, role) -> User:
        """Create a new user with hashed password."""
        password_hash = self.get_password_hash(password)
        user = User(
            username=username,
            password_hash=password_hash,
            role=role,
            is_active=True,
            last_password_change=datetime.now()
        )
        created_user = self._user_repo.save(user)
        
        # Log action
        if self._audit:
            self._audit.log_action(
                entity_type="USER",
                entity_id=str(created_user.id),
                action="CREATED",
                user="admin",
                details=f"User {username} created with role {role.value}"
            )
        
        return created_user

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return self._user_repo.get_by_username(username)

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return self._user_repo.get_by_id(user_id)

    def list_users(self):
        """List all users."""
        return self._user_repo.list_all()

    def update_user(self, user: User) -> User:
        """Update a user."""
        updated_user = self._user_repo.save(user)
        
        # Log action
        if self._audit:
            self._audit.log_action(
                entity_type="USER",
                entity_id=str(user.id),
                action="UPDATED",
                user="admin",
                details=f"User {user.username} updated"
            )
        
        return updated_user

    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        user = self._user_repo.get_by_id(user_id)
        result = self._user_repo.delete(user_id)
        
        # Log action
        if result and self._audit and user:
            self._audit.log_action(
                entity_type="USER",
                entity_id=str(user_id),
                action="DELETED",
                user="admin",
                details=f"User {user.username} deleted"
            )
        
        return result

    def unlock_user(self, user_id: int) -> bool:
        """Unlock a locked user account (admin action)."""
        user = self._user_repo.get_by_id(user_id)
        if not user:
            return False
        
        user.locked_until = None
        user.failed_login_attempts = 0
        self._user_repo.save(user)
        
        # Log action
        if self._audit:
            self._audit.log_action(
                entity_type="USER",
                entity_id=str(user_id),
                action="UNLOCKED",
                user="admin",
                details=f"User {user.username} manually unlocked"
            )
        
        return True

    def get_security_stats(self) -> dict:
        """Get security statistics for admin dashboard."""
        users = self.list_users()
        
        active_users = sum(1 for u in users if u.is_active)
        inactive_users = len(users) - active_users
        locked_users = sum(1 for u in users if u.locked_until and u.locked_until > datetime.now())
        
        stats = {
            "total_users": len(users),
            "active_users": active_users,
            "inactive_users": inactive_users,
            "locked_users": locked_users,
            "password_expiring_soon": 0,
            "recent_logins_24h": 0,
            "failed_logins_24h": 0
        }
        
        # Count password expiring in next 7 days
        for user in users:
            if user.last_password_change:
                days_since = (datetime.now() - user.last_password_change).days
                if PASSWORD_EXPIRY_DAYS - days_since <= 7 and PASSWORD_EXPIRY_DAYS - days_since > 0:
                    stats["password_expiring_soon"] += 1
        
        # Count recent login activity
        if self._login_attempt_repo:
            recent_attempts = self._login_attempt_repo.get_recent_activity(limit=1000)
            cutoff_24h = datetime.now() - timedelta(hours=24)
            
            for attempt in recent_attempts:
                if attempt.attempted_at >= cutoff_24h:
                    if attempt.success:
                        stats["recent_logins_24h"] += 1
                    else:
                        stats["failed_logins_24h"] += 1
        
        return stats
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self._user_repo.get_by_email(email)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self._user_repo.get_by_id(user_id)
    
    def change_user_password(self, user_id: int, new_password: str) -> None:
        """
        Change user password (admin or password reset).
        
        Args:
            user_id: User ID
            new_password: New password (plain text, will be hashed)
        
        Raises:
            ValueError: If password doesn't meet requirements
        """
        # Validate password strength
        if not self.validate_password_strength(new_password):
            raise ValueError("Password doesn't meet strength requirements")
        
        # Hash new password
        new_hash = self.hash_password(new_password)
        
        # Update password
        user = self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        user.password_hash = new_hash
        user.last_password_change = datetime.now()
        user.failed_login_attempts = 0  # Reset failed attempts
        user.locked_until = None  # Unlock if was locked
        
        self._user_repo.update(user)
        
        # Save to password history if available
        if self._password_history_repo:
            history = PasswordHistory(
                user_id=user_id,
                password_hash=new_hash,
                created_at=datetime.now()
            )
            self._password_history_repo.create(history)
