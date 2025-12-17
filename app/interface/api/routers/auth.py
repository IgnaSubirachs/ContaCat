from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List

from app.domain.auth.services import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
from app.domain.auth.dependencies import get_auth_service, get_current_active_user, require_role
from app.domain.auth.entities import User, UserRole
from app.domain.auth.schemas import (
    Token, UserCreate, UserUpdate, UserResponse,
    PasswordChangeRequest, UserSessionResponse, UserProfileResponse,
    SecurityAlertResponse, ActivityStatsResponse
)

from app.interface.api.templates import templates

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    remember_me: bool = False,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login endpoint with session tracking and security checks."""
    username = form_data.username
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Check account lockout
    is_locked, locked_until = auth_service.check_account_lockout(username)
    if is_locked:
        minutes_left = int((locked_until - datetime.now()).total_seconds() / 60)
        auth_service.record_login_attempt(
            username, ip_address, user_agent, False, 
            f"Account locked until {locked_until}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked. Try again in {minutes_left} minutes.",
        )
    
    # Authenticate user
    user = auth_service.authenticate_user(username, form_data.password)
    
    if not user:
        # Record failed attempt
        auth_service.record_login_attempt(
            username, ip_address, user_agent, False, 
            "Invalid credentials"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check password expiry
    is_expired, days_left = auth_service.check_password_expiry(user)
    if is_expired:
        auth_service.record_login_attempt(
            username, ip_address, user_agent, False,
            "Password expired"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your password has expired. Please contact an administrator.",
        )
    
    # Create access token
    expire_minutes = 60 * 24 * 7 if remember_me else ACCESS_TOKEN_EXPIRE_MINUTES
    access_token_expires = timedelta(minutes=expire_minutes)
    
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Create session tracking
    auth_service.create_session(
        user_id=user.id,
        token=access_token,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    # Record successful login
    auth_service.record_login_attempt(
        username, ip_address, user_agent, True
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

@router.get("/me/profile", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get extended user profile with sessions and activity."""
    sessions = auth_service.get_active_sessions(current_user.id)
    is_expired, days_left = auth_service.check_password_expiry(current_user)
    
    return UserProfileResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_password_change=current_user.last_password_change,
        password_expires_in_days=days_left if not is_expired else 0,
        active_sessions_count=len(sessions),
        last_login=sessions[0].last_activity if sessions else None
    )

@router.get("/me/sessions", response_model=List[UserSessionResponse])
async def get_my_sessions(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get all active sessions for current user."""
    sessions = auth_service.get_active_sessions(current_user.id)
    
    # Get current token to mark current session
    from app.domain.auth.dependencies import get_token_from_cookie_or_header
    current_token = await get_token_from_cookie_or_header(request)
    
    return [
        UserSessionResponse(
            id=s.id,
            user_id=s.user_id,
            ip_address=s.ip_address,
            user_agent=s.user_agent,
            device_info=s.device_info,
            created_at=s.created_at,
            last_activity=s.last_activity,
            is_active=s.is_active,
            is_current=(s.token == current_token)
        )
        for s in sessions
    ]

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Revoke a specific session."""
    session = auth_service._session_repo.get_by_id(session_id) if auth_service._session_repo else None
    
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    success = auth_service.revoke_session(session_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to revoke session")
    
    return {"message": "Session revoked successfully"}

@router.post("/me/change-password")
async def change_my_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Change current user's password."""
    success, error = auth_service.change_password(
        current_user,
        password_data.current_password,
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=error)
    
    return {"message": "Password changed successfully"}

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
    # Validate password strength
    is_valid, error = auth_service.validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
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
        # Validate password if being changed
        is_valid, error = auth_service.validate_password_strength(user_data.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        user.password_hash = auth_service.get_password_hash(user_data.password)
        user.last_password_change = datetime.now()
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

@router.post("/admin/unlock-user/{user_id}")
async def unlock_user(
    user_id: int,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Unlock a locked user account (admin only)."""
    success = auth_service.unlock_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User unlocked successfully"}

@router.get("/admin/activity", response_model=ActivityStatsResponse)
async def get_activity_stats(
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Get security activity statistics (admin only)."""
    stats = auth_service.get_security_stats()
    return ActivityStatsResponse(**stats)

@router.get("/admin/security-alerts", response_model=List[SecurityAlertResponse])
async def get_security_alerts(
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Get security alerts (admin only)."""
    alerts = []
    users = auth_service.list_users()
    
    # Check for locked accounts
    for user in users:
        if user.locked_until and user.locked_until > datetime.now():
            alerts.append(SecurityAlertResponse(
                alert_type="locked_account",
                user_id=user.id,
                username=user.username,
                message=f"Account locked until {user.locked_until.strftime('%H:%M')}",
                severity="high",
                timestamp=user.locked_until
            ))
    
    # Check for expiring passwords
    for user in users:
        if user.last_password_change:
            is_expired, days_left = auth_service.check_password_expiry(user)
            if not is_expired and days_left <= 7:
                alerts.append(SecurityAlertResponse(
                    alert_type="password_expiry",
                    user_id=user.id,
                    username=user.username,
                    message=f"Password expires in {days_left} days",
                    severity="medium" if days_left > 3 else "high",
                    timestamp=datetime.now()
                ))
    
    # Sort by severity and timestamp
    severity_order = {"high": 0, "medium": 1, "low": 2}
    alerts.sort(key=lambda x: (severity_order[x.severity], x.timestamp), reverse=True)
    
    return alerts

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

@router.get("/profile-page", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Render user profile page."""
    return templates.TemplateResponse("auth/profile.html", {"request": request})

@router.get("/admin-dashboard-page", response_class=HTMLResponse)
async def admin_dashboard_page(
    request: Request,
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Render admin security dashboard (admin only)."""
    return templates.TemplateResponse("auth/admin_dashboard.html", {"request": request})

@router.get("/logout")
async def logout():
    """Logout user by clearing the cookie."""
    from fastapi.responses import RedirectResponse
    response = RedirectResponse(url="/auth/login-page", status_code=302)
    response.delete_cookie("access_token")
    return response

# Password Recovery Endpoints
@router.post("/forgot-password")
async def forgot_password(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Request password reset email."""
    from app.domain.auth.schemas import ForgotPasswordRequest
    from app.infrastructure.email.email_service import EmailService
    from app.infrastructure.persistence.auth.password_reset_repository import SqlAlchemyPasswordResetTokenRepository
    from app.infrastructure.db.base import SessionLocal
    from app.domain.auth.entities import PasswordResetToken
    from datetime import datetime, timedelta
    import secrets
    
    # Get email from form data
    form = await request.form()
    email = form.get("email")
    
    if not email:
        return templates.TemplateResponse("auth/forgot_password.html", {
            "request": request,
            "error": "Si us plau, introdueix el teu email"
        })
    
    # Find user by email
    user = auth_service.get_user_by_email(email)
    
    # Always show same message (security: don't reveal if email exists)
    success_message = "Si l'email existeix al sistema, rebràs un correu amb instruccions per restablir la contrasenya."
    
    if user:
        # Check rate limiting
        db = SessionLocal()
        reset_repo = SqlAlchemyPasswordResetTokenRepository(db)
        recent_count = reset_repo.count_recent_requests(user.id, 60)  # Last hour
        
        if recent_count >= 3:
            # Rate limited - but don't tell user
            return templates.TemplateResponse("auth/forgot_password.html", {
                "request": request,
                "success": success_message
            })
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(minutes=30)
        
        # Save token to database
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        reset_repo.create(reset_token)
        db.close()
        
        # Send email
        reset_link = f"http://{request.headers.get('host', 'localhost:8000')}/auth/reset-password-page/{token}"
        email_service = EmailService()
        email_service.send_password_reset_email(email, reset_link, user.username)
    
    return templates.TemplateResponse("auth/forgot_password.html", {
        "request": request,
        "success": success_message
    })

@router.post("/reset-password")
async def reset_password(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reset password with token."""
    from app.domain.auth.schemas import ResetPasswordRequest
    from app.infrastructure.persistence.auth.password_reset_repository import SqlAlchemyPasswordResetTokenRepository
    from app.infrastructure.db.base import SessionLocal
    from datetime import datetime
    
    # Get form data
    form = await request.form()
    token = form.get("token")
    new_password = form.get("new_password")
    confirm_password = form.get("confirm_password")
    
    if not all([token, new_password, confirm_password]):
        return templates.TemplateResponse("auth/reset_password.html", {
            "request": request,
            "token": token,
            "error": "Tots els camps són obligatoris"
        })
    
    if new_password != confirm_password:
        return templates.TemplateResponse("auth/reset_password.html", {
            "request": request,
            "token": token,
            "error": "Les contrasenyes no coincideixen"
        })
    
    # Validate token
    db = SessionLocal()
    reset_repo = SqlAlchemyPasswordResetTokenRepository(db)
    reset_token = reset_repo.get_by_token(token)
    
    if not reset_token:
        return templates.TemplateResponse("auth/reset_password.html", {
            "request": request,
            "token": token,
            "error": "Token invàlid o expirat"
        })
    
    if reset_token.used:
        return templates.TemplateResponse("auth/reset_password.html", {
            "request": request,
            "token": token,
            "error": "Aquest token ja ha estat utilitzat"
        })
    
    if reset_token.expires_at < datetime.now():
        return templates.TemplateResponse("auth/reset_password.html", {
            "request": request,
            "token": token,
            "error": "Aquest token ha expirat"
        })
    
    # Update password
    user = auth_service.get_user_by_id(reset_token.user_id)
    if not user:
        return templates.TemplateResponse("auth/reset_password.html", {
            "request": request,
            "token": token,
            "error": "Usuari no trobat"
        })
    
    # Change password
    try:
        auth_service.change_user_password(user.id, new_password)
        reset_repo.mark_as_used(reset_token.id)
        db.close()
        
        return templates.TemplateResponse("auth/reset_password.html", {
            "request": request,
            "success": "Contrasenya restablerta correctament! Ara pots iniciar sessió."
        })
    except ValueError as e:
        return templates.TemplateResponse("auth/reset_password.html", {
            "request": request,
            "token": token,
            "error": str(e)
        })

@router.get("/reset-password-page/{token}", response_class=HTMLResponse)
async def reset_password_page(
    request: Request,
    token: str
):
    """Display password reset form."""
    from app.infrastructure.persistence.auth.password_reset_repository import SqlAlchemyPasswordResetTokenRepository
    from app.infrastructure.db.base import SessionLocal
    from datetime import datetime
    
    # Validate token exists and not expired
    db = SessionLocal()
    reset_repo = SqlAlchemyPasswordResetTokenRepository(db)
    reset_token = reset_repo.get_by_token(token)
    db.close()
    
    if not reset_token or reset_token.used or reset_token.expires_at < datetime.now():
        return templates.TemplateResponse("auth/reset_password.html", {
            "request": request,
            "error": "Token invàlid o expirat"
        })
    
    return templates.TemplateResponse("auth/reset_password.html", {
        "request": request,
        "token": token
    })

@router.get("/forgot-password-page", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    """Display forgot password form."""
    return templates.TemplateResponse("auth/forgot_password.html", {"request": request})
