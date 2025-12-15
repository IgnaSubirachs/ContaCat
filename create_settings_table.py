import sys
import os

sys.path.insert(0, os.getcwd())

from app.infrastructure.db.base import Base, engine
from app.infrastructure.persistence.settings.models import CompanySettingsModel

def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

if __name__ == "__main__":
    create_tables()
