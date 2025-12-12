from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.infrastructure.db.base import get_db
from app.infrastructure.persistence.auth.repositories import SqlAlchemyUserRepository
from app.domain.auth.services import AuthService
from app.domain.auth.entities import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

async def get_token_from_cookie_or_header(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    access_token: Optional[str] = Cookie(None)
) -> Optional[str]:
    """Get JWT token from Authorization header or cookie."""
    if token:
        return token
    if access_token:
        return access_token
    return None


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency to get AuthService instance."""
    user_repo = SqlAlchemyUserRepository(db)
    return AuthService(user_repo)

async def get_current_user(
    token: Optional[str] = Depends(get_token_from_cookie_or_header),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    payload = auth_service.decode_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = auth_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_user_or_redirect(
    token: Optional[str] = Depends(get_token_from_cookie_or_header),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """Get current user or return None (for redirect handling)."""
    if not token:
        return None
    
    payload = auth_service.decode_token(token)
    if payload is None:
        return None
    
    username: str = payload.get("sub")
    if username is None:
        return None
    
    user = auth_service.get_user_by_username(username)
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_role(*allowed_roles: UserRole):
    """Dependency factory to check if user has required role."""
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

# Module access permissions
MODULE_PERMISSIONS = {
    "partners": [UserRole.ADMIN, UserRole.MANAGER, UserRole.USER, UserRole.READ_ONLY],
    "employees": [UserRole.ADMIN, UserRole.MANAGER, UserRole.READ_ONLY],
    "accounts": [UserRole.ADMIN, UserRole.MANAGER, UserRole.READ_ONLY],
    "accounting": [UserRole.ADMIN, UserRole.MANAGER, UserRole.READ_ONLY],
    "fiscal": [UserRole.ADMIN, UserRole.MANAGER],
    "assets": [UserRole.ADMIN, UserRole.MANAGER, UserRole.READ_ONLY],
    "quotes": [UserRole.ADMIN, UserRole.MANAGER, UserRole.USER, UserRole.READ_ONLY],
    "sales_orders": [UserRole.ADMIN, UserRole.MANAGER, UserRole.USER, UserRole.READ_ONLY],
    "sales_invoices": [UserRole.ADMIN, UserRole.MANAGER, UserRole.USER, UserRole.READ_ONLY],
    "inventory": [UserRole.ADMIN, UserRole.MANAGER, UserRole.USER, UserRole.READ_ONLY],
    "analytics": [UserRole.ADMIN, UserRole.MANAGER, UserRole.READ_ONLY],
    "users": [UserRole.ADMIN],
}


def can_access_module(user: User, module: str) -> bool:
    """Check if user can access a specific module."""
    allowed_roles = MODULE_PERMISSIONS.get(module, [])
    return user.role in allowed_roles
