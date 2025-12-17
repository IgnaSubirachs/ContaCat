"""SQL Alchemy implementation of PasswordResetTokenRepository."""
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.domain.auth.repositories import PasswordResetTokenRepository
from app.domain.auth.entities import PasswordResetToken
from app.infrastructure.persistence.auth.models import PasswordResetTokenModel


class SqlAlchemyPasswordResetTokenRepository(PasswordResetTokenRepository):
    """SQLAlchemy implementation of password reset token repository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, token: PasswordResetToken) -> PasswordResetToken:
        """Create a password reset token."""
        db_token = PasswordResetTokenModel(
            user_id=token.user_id,
            token=token.token,
            expires_at=token.expires_at,
            used=token.used,
            created_at=token.created_at
        )
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        
        return PasswordResetToken(
            id=db_token.id,
            user_id=db_token.user_id,
            token=db_token.token,
            expires_at=db_token.expires_at,
            used=db_token.used,
            created_at=db_token.created_at
        )
    
    def get_by_token(self, token_str: str) -> Optional[PasswordResetToken]:
        """Get a password reset token by token string."""
        db_token = self.db.query(PasswordResetTokenModel).filter(
            PasswordResetTokenModel.token == token_str
        ).first()
        
        if not db_token:
            return None
        
        return PasswordResetToken(
            id=db_token.id,
            user_id=db_token.user_id,
            token=db_token.token,
            expires_at=db_token.expires_at,
            used=db_token.used,
            created_at=db_token.created_at
        )
    
    def mark_as_used(self, token_id: int) -> None:
        """Mark a token as used."""
        self.db.query(PasswordResetTokenModel).filter(
            PasswordResetTokenModel.id == token_id
        ).update({"used": True})
        self.db.commit()
    
    def cleanup_expired(self) -> int:
        """Cleanup expired tokens. Returns count of deleted tokens."""
        now = datetime.now()
        result = self.db.query(PasswordResetTokenModel).filter(
            PasswordResetTokenModel.expires_at < now
        ).delete()
        self.db.commit()
        return result
    
    def count_recent_requests(self, user_id: int, minutes: int) -> int:
        """Count recent reset requests for rate limiting."""
        since = datetime.now() - timedelta(minutes=minutes)
        count = self.db.query(PasswordResetTokenModel).filter(
            PasswordResetTokenModel.user_id == user_id,
            PasswordResetTokenModel.created_at >= since
        ).count()
        return count
