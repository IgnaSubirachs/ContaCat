"""
Script to add necessary accounts for sales module.
Creates the required accounts in the chart of accounts if they don't exist.
"""
import sys
import os
from decimal import Decimal

sys.path.append(os.getcwd())

from app.infrastructure.db.base import SessionLocal
from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository
from app.domain.accounts.entities import Account, AccountType


def add_sales_accounts():
    """Add necessary accounts for sales module."""
    print("\n" + "="*60)
    print("ADDING SALES ACCOUNTS")
    print("="*60 + "\n")
    
    try:
        # Initialize repository
        account_repo = SqlAlchemyAccountRepository(SessionLocal)
        
        # Define accounts to create
        accounts_to_create = [
            {
                "code": "43000000",
                "name": "Clients (Customers Receivable)",
                "account_type": AccountType.ASSET,
                "group": 4,
                "parent_code": None
            },
            {
                "code": "70000000",
                "name": "Vendes de mercaderies (Sales Revenue)",
                "account_type": AccountType.INCOME,
                "group": 7,
                "parent_code": None
            },
            {
                "code": "47700000",
                "name": "HP IVA repercutit (VAT Payable)",
                "account_type": AccountType.LIABILITY,
                "group": 4,
                "parent_code": None
            }
        ]
        
        # Create accounts if they don't exist
        for acc_data in accounts_to_create:
            existing = account_repo.find_by_code(acc_data["code"])
            if existing:
                print(f"[EXISTS] Account {acc_data['code']} - {acc_data['name']}")
            else:
                account = Account(
                    code=acc_data["code"],
                    name=acc_data["name"],
                    account_type=acc_data["account_type"],
                    group=acc_data["group"],
                    parent_code=acc_data["parent_code"]
                )
                account_repo.add(account)
                print(f"[CREATED] Account {acc_data['code']} - {acc_data['name']}")
        
        print("\n[OK] Sales accounts setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = add_sales_accounts()
    sys.exit(0 if success else 1)
