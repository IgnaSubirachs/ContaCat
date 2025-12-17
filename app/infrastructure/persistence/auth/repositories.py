from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.domain.auth.entities import User, UserRole, UserSession, PasswordHistory, LoginAttempt
from app.domain.auth.repositories import (
    UserRepository, UserSessionRepository, 
    PasswordHistoryRepository, LoginAttemptRepository
)
from app.infrastructure.persistence.auth.models import (
    UserModel, UserSessionModel, PasswordHistoryModel, LoginAttemptModel
)

class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            password_hash=model.password_hash,
            role=model.role,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_password_change=model.last_password_change,
            failed_login_attempts=model.failed_login_attempts,
            locked_until=model.locked_until
        )

    def _to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            username=entity.username,
            password_hash=entity.password_hash,
            role=entity.role,
            is_active=entity.is_active
        )

    def save(self, user: User) -> User:
        model = self._to_model(user)
        if user.id:
            existing = self.db.query(UserModel).filter(UserModel.id == user.id).first()
            if existing:
                existing.username = user.username
                existing.password_hash = user.password_hash
                existing.role = user.role
                existing.is_active = user.is_active
                existing.last_password_change = user.last_password_change
                existing.failed_login_attempts = user.failed_login_attempts
                existing.locked_until = user.locked_until
                model = existing
        else:
            self.db.add(model)
        
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, user_id: int) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(model) if model else None

    def get_by_username(self, username: str) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.username == username).first()
        return self._to_entity(model) if model else None

    def list_all(self) -> List[User]:
        models = self.db.query(UserModel).all()
        return [self._to_entity(m) for m in models]

    def delete(self, user_id: int) -> bool:
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if model:
            self.db.delete(model)
            self.db.commit()
            return True
        return False
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        model = self.db.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(model) if model else None
    
    def update(self, user: User) -> User:
        """Update existing user."""
        existing = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if not existing:
            raise ValueError(f"User with id {user.id} not found")
        
        existing.username = user.username
        existing.email = user.email
        existing.password_hash = user.password_hash
        existing.role = user.role
        existing.is_active = user.is_active
        existing.last_password_change = user.last_password_change
        existing.failed_login_attempts = user.failed_login_attempts
        existing.locked_until = user.locked_until
        
        self.db.commit()
        self.db.refresh(existing)
        return self._to_entity(existing)

class SqlAlchemyUserSessionRepository(UserSessionRepository):
    """SQLAlchemy implementation of UserSessionRepository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_entity(self, model: UserSessionModel) -> UserSession:
        return UserSession(
            id=model.id,
            user_id=model.user_id,
            token=model.token,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            device_info=model.device_info,
            created_at=model.created_at,
            last_activity=model.last_activity,
            is_active=model.is_active
        )
    
    def save(self, session: UserSession) -> UserSession:
        model = UserSessionModel(
            id=session.id,
            user_id=session.user_id,
            token=session.token,
            ip_address=session.ip_address,
            user_agent=session.user_agent,
            device_info=session.device_info,
            is_active=session.is_active
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)
    
    def get_by_id(self, session_id: str) -> Optional[UserSession]:
        model = self.db.query(UserSessionModel).filter(
            UserSessionModel.id == session_id
        ).first()
        return self._to_entity(model) if model else None
    
    def get_active_sessions(self, user_id: int) -> List[UserSession]:
        models = self.db.query(UserSessionModel).filter(
            UserSessionModel.user_id == user_id,
            UserSessionModel.is_active == True
        ).all()
        return [self._to_entity(m) for m in models]
    
    def revoke_session(self, session_id: str) -> bool:
        model = self.db.query(UserSessionModel).filter(
            UserSessionModel.id == session_id
        ).first()
        if model:
            model.is_active = False
            self.db.commit()
            return True
        return False
    
    def update_last_activity(self, session_id: str) -> bool:
        model = self.db.query(UserSessionModel).filter(
            UserSessionModel.id == session_id
        ).first()
        if model:
            model.last_activity = datetime.now()
            self.db.commit()
            return True
        return False
    
    def cleanup_expired_sessions(self, hours: int) -> int:
        cutoff = datetime.now() - timedelta(hours=hours)
        deleted = self.db.query(UserSessionModel).filter(
            UserSessionModel.last_activity < cutoff
        ).delete()
        self.db.commit()
        return deleted

class SqlAlchemyPasswordHistoryRepository(PasswordHistoryRepository):
    """SQLAlchemy implementation of PasswordHistoryRepository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_entity(self, model: PasswordHistoryModel) -> PasswordHistory:
        return PasswordHistory(
            id=model.id,
            user_id=model.user_id,
            password_hash=model.password_hash,
            created_at=model.created_at
        )
    
    def save(self, password_history: PasswordHistory) -> PasswordHistory:
        model = PasswordHistoryModel(
            user_id=password_history.user_id,
            password_hash=password_history.password_hash
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)
    
    def get_recent_passwords(self, user_id: int, count: int) -> List[PasswordHistory]:
        models = self.db.query(PasswordHistoryModel).filter(
            PasswordHistoryModel.user_id == user_id
        ).order_by(desc(PasswordHistoryModel.created_at)).limit(count).all()
        return [self._to_entity(m) for m in models]

class SqlAlchemyLoginAttemptRepository(LoginAttemptRepository):
    """SQLAlchemy implementation of LoginAttemptRepository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_entity(self, model: LoginAttemptModel) -> LoginAttempt:
        return LoginAttempt(
            id=model.id,
            username=model.username,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            success=model.success,
            attempted_at=model.attempted_at,
            failure_reason=model.failure_reason
        )
    
    def save(self, attempt: LoginAttempt) -> LoginAttempt:
        model = LoginAttemptModel(
            username=attempt.username,
            ip_address=attempt.ip_address,
            user_agent=attempt.user_agent,
            success=attempt.success,
            failure_reason=attempt.failure_reason
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)
    
    def get_recent_attempts(self, username: str, minutes: int) -> List[LoginAttempt]:
        cutoff = datetime.now() - timedelta(minutes=minutes)
        models = self.db.query(LoginAttemptModel).filter(
            LoginAttemptModel.username == username,
            LoginAttemptModel.attempted_at >= cutoff
        ).order_by(desc(LoginAttemptModel.attempted_at)).all()
        return [self._to_entity(m) for m in models]
    
    def get_failed_attempts_count(self, username: str, minutes: int) -> int:
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return self.db.query(LoginAttemptModel).filter(
            LoginAttemptModel.username == username,
            LoginAttemptModel.success == False,
            LoginAttemptModel.attempted_at >= cutoff
        ).count()
    
    def get_recent_activity(self, limit: int = 100) -> List[LoginAttempt]:
        models = self.db.query(LoginAttemptModel).order_by(
            desc(LoginAttemptModel.attempted_at)
        ).limit(limit).all()
        return [self._to_entity(m) for m in models]
