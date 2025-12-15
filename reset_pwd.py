from sqlalchemy import text
from app.infrastructure.db.database import get_db, SessionLocal
from app.domain.auth.services import AuthService
from app.infrastructure.persistence.auth.repositories import SqlAlchemyUserRepository
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def reset_password(username, new_password):
    db = SessionLocal()
    try:
        hashed = pwd_context.hash(new_password)
        db.execute(text("UPDATE users SET password_hash = :pwd WHERE username = :user"), {"pwd": hashed, "user": username})
        db.commit()
        print(f"Password for {username} reset successfully to '{new_password}'.")
    except Exception as e:
        print(f"Error resetting password: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_password("Ignasi", "Vinyet_2024")
    reset_password("admin", "admin")
