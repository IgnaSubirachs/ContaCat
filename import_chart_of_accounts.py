"""
Import Spanish Chart of Accounts (Plan General Contable)
Imports all accounts from chart_of_accounts_es.json into the database.
"""
import sys
import os
import json

sys.path.append(os.getcwd())

from app.infrastructure.db.base import SessionLocal
from app.domain.accounts.entities import Account, AccountType
from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository


def import_chart_of_accounts():
    """Import Spanish chart of accounts from JSON file."""
    print("\n" + "="*60)
    print("IMPORTING SPANISH CHART OF ACCOUNTS (PGC)")
    print("="*60 + "\n")
    
    try:
        # Load JSON file
        json_file = "chart_of_accounts_es.json"
        print(f"[*] Loading accounts from {json_file}...")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            accounts_data = json.load(f)
        
        print(f"[OK] Loaded {len(accounts_data)} accounts\n")
        
        # Initialize repository
        account_repo = SqlAlchemyAccountRepository(SessionLocal)
        
        # Import accounts
        created_count = 0
        skipped_count = 0
        
        for acc_data in accounts_data:
            try:
                # Check if account already exists
                existing = account_repo.find_by_code(acc_data["code"])
                if existing:
                    print(f"[SKIP] {acc_data['code']} - {acc_data['name']} (already exists)")
                    skipped_count += 1
                    continue
                
                # Create account
                account = Account(
                    code=acc_data["code"],
                    name=acc_data["name"],
                    account_type=AccountType[acc_data["type"]],
                    group=acc_data["group"]
                )
                
                account_repo.add(account)
                print(f"[OK] {acc_data['code']} - {acc_data['name']}")
                created_count += 1
                
            except Exception as e:
                print(f"[ERROR] Failed to import {acc_data['code']}: {e}")
        
        print("\n" + "="*60)
        print("IMPORT SUMMARY")
        print("="*60)
        print(f"Total accounts in file: {len(accounts_data)}")
        print(f"Created: {created_count}")
        print(f"Skipped (already exist): {skipped_count}")
        print("\n[OK] Chart of accounts import completed!")
        
        return True
        
    except FileNotFoundError:
        print(f"[ERROR] File {json_file} not found!")
        return False
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = import_chart_of_accounts()
    sys.exit(0 if success else 1)
