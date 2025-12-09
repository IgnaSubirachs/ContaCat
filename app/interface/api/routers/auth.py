from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List

from app.domain.auth.services import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
from app.domain.auth.dependencies import get_auth_service, get_current_active_user, require_role
from app.domain.auth.entities import User, UserRole
from app.domain.auth.schemas import Token, UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/interface/web/templates")

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login endpoint that returns a JWT token."""
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role.value,
        is_active=current_user.is_active
    )

# Admin-only endpoints
@router.get("/users", response_model=List[UserResponse])
async def list_users(
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """List all users (admin only)."""
    users = auth_service.list_users()
    return [
        UserResponse(
            id=u.id,
            username=u.username,
            role=u.role.value,
            is_active=u.is_active
        )
        for u in users
    ]

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Create a new user (admin only)."""
    # Check if username already exists
    existing_user = auth_service.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    user = auth_service.create_user(
        username=user_data.username,
        password=user_data.password,
        role=user_data.role
    )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role.value,
        is_active=user.is_active
    )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Update a user (admin only)."""
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_data.username is not None:
        user.username = user_data.username
    if user_data.password is not None:
        user.password_hash = auth_service.get_password_hash(user_data.password)
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    updated_user = auth_service.update_user(user)
    
    return UserResponse(
        id=updated_user.id,
        username=updated_user.username,
        role=updated_user.role.value,
        is_active=updated_user.is_active
    )

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Delete a user (admin only)."""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = auth_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

# Web interface endpoints
@router.get("/login-page", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render login page."""
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/users-page", response_class=HTMLResponse)
async def users_page(
    request: Request,
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Render user management page (admin only)."""
    return templates.TemplateResponse("auth/users.html", {"request": request})

@router.get("/logout")
async def logout():
    """Logout user by clearing the cookie."""
    from fastapi.responses import RedirectResponse
    response = RedirectResponse(url="/auth/login-page", status_code=302)
    response.delete_cookie("access_token")
    return response
