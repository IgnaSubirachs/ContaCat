import sys
import os

from app.infrastructure.db.base import Base, engine
from app.infrastructure.persistence.budgets.models import BudgetModel, BudgetLineModel

def init_budgets_db():
    print("Creating Budgets tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_budgets_db()
