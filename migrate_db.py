import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import text
from app.infrastructure.db.base import engine

def migrate():
    print("Migrating database schema...")
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE journal_entries ADD COLUMN attachment_path VARCHAR(255) NULL;"))
            conn.commit()
            print("Successfully added attachment_path column.")
        except Exception as e:
            print(f"Migration failed or column already exists: {e}")

if __name__ == "__main__":
    migrate()
