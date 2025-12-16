"""
Add SMTP configuration columns to company_settings table.
Run this script to update existing database.
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./erp.db")
engine = create_engine(DATABASE_URL)

def migrate():
    print("Adding SMTP configuration columns to company_settings...")
    
    with engine.connect() as conn:
        # Check if columns exist first (avoid errors on re-run)
        try:
            conn.execute(text("SELECT smtp_host FROM company_settings LIMIT 1"))
            print("✓ SMTP columns already exist")
            return
        except:
            pass  # Columns don't exist, proceed with migration
        
        # Add new columns
        try:
            conn.execute(text("""
                ALTER TABLE company_settings ADD COLUMN smtp_host VARCHAR(255)
            """))
            conn.execute(text("""
                ALTER TABLE company_settings ADD COLUMN smtp_port INTEGER DEFAULT 587
            """))
            conn.execute(text("""
                ALTER TABLE company_settings ADD COLUMN smtp_user VARCHAR(255)
            """))
            conn.execute(text("""
                ALTER TABLE company_settings ADD COLUMN smtp_password VARCHAR(500)
            """))
            conn.execute(text("""
                ALTER TABLE company_settings ADD COLUMN smtp_from_email VARCHAR(255)
            """))
            conn.execute(text("""
                ALTER TABLE company_settings ADD COLUMN smtp_from_name VARCHAR(255)
            """))
            conn.execute(text("""
                ALTER TABLE company_settings ADD COLUMN smtp_use_tls BOOLEAN DEFAULT 1
            """))
            conn.commit()
            print("✓ SMTP columns added successfully")
        except Exception as e:
            print(f"Error adding columns: {e}")
            conn.rollback()
            
if __name__ == "__main__":
    migrate()
