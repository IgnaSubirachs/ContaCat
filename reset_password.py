from app.infrastructure.db.base import SessionLocal
from app.infrastructure.persistence.auth.repositories import SqlAlchemyUserRepository
from app.domain.auth.services import AuthService

def reset_admin_password():
    db = SessionLocal()
    try:
        print("Resetting admin password...")
        user_repo = SqlAlchemyUserRepository(db)
        auth_service = AuthService(user_repo)
        
        user = auth_service.get_user_by_username("admin")
        if user:
            # Force new hash generation with fixed libraries
            new_hash = auth_service.get_password_hash("admin123")
            user.password_hash = new_hash
            user_repo.save(user)
            print("[SUCCESS] Admin password reset to: admin123")
        else:
            print("[ERROR] Admin user not found!")
            
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()
