import sys
import os
from datetime import date
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.domain.accounts.entities import Account, AccountType
from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository
from app.domain.accounts.services import AccountService
from app.domain.accounting.services import AccountingService
from app.infrastructure.persistence.accounting.repository import SqlAlchemyJournalRepository
from app.infrastructure.db.base import Base, engine

def verify_modules():
    print("1. Initializing Database...")
    Base.metadata.create_all(bind=engine)
    
    # Repositories
    account_repo = SqlAlchemyAccountRepository()
    journal_repo = SqlAlchemyJournalRepository()
    
    # Services
    account_service = AccountService(account_repo)
    accounting_service = AccountingService(account_repo, journal_repo)
    
    print("\n2. Testing Accounts Module...")
    try:
        # Create accounts
        print("   Creating accounts...")
        try:
            account_service.create_account("4300001", "Client A", AccountType.ASSET, 4)
            print("   - Created Client A (4300001)")
        except ValueError as e:
            print(f"   - Client A already exists: {e}")

        try:
            account_service.create_account("7000001", "Vendes A", AccountType.INCOME, 7)
            print("   - Created Vendes A (7000001)")
        except ValueError as e:
            print(f"   - Vendes A already exists: {e}")
            
        try:
            account_service.create_account("5720001", "Banc Sabadell", AccountType.ASSET, 5)
            print("   - Created Banc Sabadell (5720001)")
        except ValueError as e:
            print(f"   - Banc Sabadell already exists: {e}")

        # List accounts
        accounts = account_service.list_accounts()
        print(f"   Total accounts: {len(accounts)}")
        
    except Exception as e:
        print(f"   ERROR in Accounts Module: {e}")
        return

    print("\n3. Testing Accounting Module...")
    try:
        # Create Journal Entry (Invoice)
        print("   Creating Invoice Entry...")
        entry = accounting_service.create_journal_entry(
            entry_date=date.today(),
            description="Factura Venda Client A",
            lines=[
                ("4300001", Decimal("121.00"), Decimal("0.00"), "Factura F-001"),
                ("7000001", Decimal("0.00"), Decimal("100.00"), "Base Imposable"),
                # Assuming 477 exists or skipping for simplicity, let's just balance it with 2 lines for now or add 477
            ]
        )
        # Wait, I need to balance it. 121 vs 100. Need 21 VAT.
        # Let's create VAT account first
        try:
            account_service.create_account("4770001", "HP IVA Repercutit", AccountType.LIABILITY, 4)
        except:
            pass
            
        # Retry with VAT
        entry = accounting_service.create_journal_entry(
            entry_date=date.today(),
            description="Factura Venda Client A",
            lines=[
                ("4300001", Decimal("121.00"), Decimal("0.00"), "Factura F-001"),
                ("7000001", Decimal("0.00"), Decimal("100.00"), "Base Imposable"),
                ("4770001", Decimal("0.00"), Decimal("21.00"), "IVA 21%"),
            ]
        )
        print(f"   - Created Entry #{entry.entry_number} (Status: {entry.status.value})")
        
        # Post entry
        print("   Posting Entry...")
        accounting_service.post_journal_entry(entry.id)
        print(f"   - Entry Posted (Status: {entry.status.value})")
        
        # Check Ledger
        print("   Checking Ledger for Client A (4300001)...")
        balance = accounting_service.get_account_balance("4300001")
        print(f"   - Balance: {balance} €")
        
        # Check Trial Balance
        print("   Checking Trial Balance...")
        tb = accounting_service.get_trial_balance()
        print(f"   - Trial Balance items: {len(tb)}")
        
    except Exception as e:
        print(f"   ERROR in Accounting Module: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_modules()
