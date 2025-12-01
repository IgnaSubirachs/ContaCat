from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.domain.auth.entities import User
from app.domain.auth.repositories import UserRepository

# Security configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # TODO: Move to .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self._user_repo = user_repository

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

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
            is_active=True
        )
        return self._user_repo.save(user)

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
        return self._user_repo.save(user)

    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        return self._user_repo.delete(user_id)
