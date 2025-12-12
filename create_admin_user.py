"""
Script to create the default admin user for the ERP system.
Run this after database initialization.
"""
from app.infrastructure.db.base import SessionLocal
from app.infrastructure.persistence.auth.repositories import SqlAlchemyUserRepository
from app.domain.auth.services import AuthService
from app.domain.auth.entities import UserRole

def create_admin_user():
    """Create default admin user if it doesn't exist."""
    db = SessionLocal()
    try:
        user_repo = SqlAlchemyUserRepository(db)
        auth_service = AuthService(user_repo)
        
        # Check if admin user already exists
        admin = auth_service.get_user_by_username("admin")
        if admin:
            print("✓ Admin user already exists")
            return
        
        # Create admin user
        admin = auth_service.create_user(
            username="admin",
            password="admin123",  # Change this in production!
            role=UserRole.ADMIN
        )
        
        print(f"✓ Admin user created successfully")
        print(f"  Username: admin")
        print(f"  Password: admin123")
        print(f"  ⚠️  IMPORTANT: Change the password after first login!")
        
    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
