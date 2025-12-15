import sys
import os

from app.infrastructure.db.base import Base, engine
from app.infrastructure.persistence.banking.models import BankStatementModel, BankStatementLineModel

def init_banking_db():
    print("Creating Banking tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_banking_db()
