import sys
import os

from app.infrastructure.db.base import Base, engine
from app.infrastructure.persistence.finance.models import LoanModel, AmortizationEntryModel

def init_finance_db():
    print("Creating Finance tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_finance_db()
