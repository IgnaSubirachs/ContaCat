from app.infrastructure.db.base import SessionLocal
from app.infrastructure.persistence.auth.repositories import SqlAlchemyUserRepository
from app.domain.auth.services import AuthService
from app.domain.auth.entities import UserRole

def create_custom_admin():
    db = SessionLocal()
    try:
        user_repo = SqlAlchemyUserRepository(db)
        auth_service = AuthService(user_repo)
        
        username = "Ignasi"
        password = "Vinyet_2024"
        
        # Check if user already exists
        existing_user = auth_service.get_user_by_username(username)
        
        if existing_user:
            print(f"User '{username}' already exists. Updating password...")
            # Update password
            new_hash = auth_service.get_password_hash(password)
            existing_user.password_hash = new_hash
            existing_user.role = UserRole.ADMIN # Ensure is admin
            user_repo.save(existing_user)
            print(f"[SUCCESS] Updated user '{username}' with new password and ADMIN role.")
        else:
            print(f"Creating new user '{username}'...")
            auth_service.create_user(
                username=username,
                password=password,
                role=UserRole.ADMIN
            )
            print(f"[SUCCESS] Created user '{username}' with ADMIN role.")
            
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_custom_admin()
