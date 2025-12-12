from sqlalchemy import text
from app.infrastructure.db.database import get_db

db = next(get_db())
try:
    result = db.execute(text("SELECT username, role FROM users")).fetchall()
    print("Users found:", result)
except Exception as e:
    print("Error querying users:", e)
