from app.domain.auth.services import pwd_context
from app.infrastructure.db.base import SessionLocal
from app.infrastructure.persistence.auth.models import UserModel

# Create hash
new_hash = pwd_context.hash("admin123")
print(f"New hash created: {new_hash}")

# Update database
db = SessionLocal()
try:
    user = db.query(UserModel).filter(UserModel.username == "admin").first()
    if user:
        user.password_hash = new_hash
        db.commit()
        print(f"Password updated for user: {user.username}")
    else:
        print("Admin user not found!")
finally:
    db.close()
