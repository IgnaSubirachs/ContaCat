"""
Database initialization script for ERP system.
Creates all tables defined in SQLAlchemy models.
"""
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.infrastructure.db.base import init_db as create_tables_func, Base

def init_database():
    """Initialize database by creating all tables."""
    print("[*] Initializing database...")
    
    try:
        # Create all tables using the function from base.py that has all imports
        create_tables_func()
        print("[OK] All tables created successfully!")
        
        # List created tables
        print("\n[*] Created tables:")
        for table in Base.metadata.sorted_tables:
            print(f"   - {table.name}")
            
    except Exception as e:
        print(f"[ERROR] Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
