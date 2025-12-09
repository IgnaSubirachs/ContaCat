import sys
import os
from datetime import date
from decimal import Decimal

# Add app to path
sys.path.append(os.getcwd())

from app.infrastructure.db.base import init_db, SessionLocal
from app.domain.assets.entities import Asset, AssetStatus, DepreciationMethod
from app.domain.accounts.entities import AccountType
from app.infrastructure.persistence.assets.repositories import SqlAlchemyAssetRepository
from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository
from app.infrastructure.persistence.accounting.repository import SqlAlchemyJournalRepository
from app.domain.assets.services import AssetService
from app.domain.accounting.services import AccountingService

def verify_integration():
    print("Initializing database...")
    init_db()
    
    session = SessionLocal()
    
    try:
        print("Setting up repositories and services...")
        asset_repo = SqlAlchemyAssetRepository(session)
        account_repo = SqlAlchemyAccountRepository(session)
        journal_repo = SqlAlchemyJournalRepository(lambda: session)
        
        accounting_service = AccountingService(account_repo, journal_repo)
        asset_service = AssetService(asset_repo, accounting_service)
        
        print("Creating necessary accounts...")
        # Create accounts if they don't exist
        accounts_to_create = [
            ("211000", "Construccions", AccountType.ASSET, 2),
            ("281000", "Amort. Acum. Construccions", AccountType.ASSET, 2), # Contra-asset, technically asset type but credit balance
            ("681000", "Amort. Immobilitzat Material", AccountType.EXPENSE, 6)
        ]
        
        for code, name, type_, group in accounts_to_create:
            if not account_repo.find_by_code(code):
                accounting_service.create_account(code, name, type_, group)
                print(f"Created account {code}")
            else:
                print(f"Account {code} already exists")
                
        print("Creating test asset...")
        asset_code = "TEST-ASSET-001"
        existing_asset = asset_repo.get_by_code(asset_code)
        if existing_asset:
            print("Asset already exists, skipping creation.")
            asset = existing_asset
        else:
            asset = Asset(
                code=asset_code,
                name="Test Building",
                description="A test building for verification",
                purchase_date=date(2024, 1, 1),
                purchase_price=10000.0,
                useful_life_years=10,
                residual_value=0.0,
                depreciation_method=DepreciationMethod.LINEAR,
                status=AssetStatus.ACTIVE,
                account_code_asset="211000",
                account_code_accumulated_depreciation="281000",
                account_code_depreciation_expense="681000"
            )
            asset = asset_service.create_asset(asset)
            print(f"Created asset {asset.code}")
            
        print("Generating depreciation for 2024...")
        # Check if already depreciated for 2024
        already_depreciated = any(entry.date.year == 2024 for entry in asset.depreciation_entries)
        
        if not already_depreciated:
            depreciation_entry = asset_service.generate_depreciation_entries(asset.id, 2024)
            print(f"Generated depreciation entry: {depreciation_entry.amount} EUR")
            
            # Verify Journal Entry
            journal_entry_number = depreciation_entry.journal_entry_id
            print(f"Linked Journal Entry Number: {journal_entry_number}")
            
            journal_entry = journal_repo.find_by_number(journal_entry_number)
            
            if journal_entry:
                print("Found Journal Entry!")
                print(f"Description: {journal_entry.description}")
                print(f"Date: {journal_entry.entry_date}")
                print("Lines:")
                for line in journal_entry.lines:
                    print(f" - {line.account_code}: Debit={line.debit}, Credit={line.credit}")
                
                # Assertions
                assert journal_entry.total_debit == Decimal("1000.0"), f"Expected total debit 1000.0, got {journal_entry.total_debit}"
                assert journal_entry.total_credit == Decimal("1000.0"), f"Expected total credit 1000.0, got {journal_entry.total_credit}"
                assert any(l.account_code == "681000" and l.debit == Decimal("1000.0") for l in journal_entry.lines), "Debit line missing or incorrect"
                assert any(l.account_code == "281000" and l.credit == Decimal("1000.0") for l in journal_entry.lines), "Credit line missing or incorrect"
                
                print("VERIFICATION SUCCESSFUL: Journal Entry created correctly.")
            else:
                print("VERIFICATION FAILED: Journal Entry not found.")
        else:
            print("Asset already depreciated for 2024. Skipping generation.")
            # Retrieve the entry to verify
            depreciation_entry = next(entry for entry in asset.depreciation_entries if entry.date.year == 2024)
            journal_entry = journal_repo.find_by_number(depreciation_entry.journal_entry_id)
            if journal_entry:
                 print("VERIFICATION SUCCESSFUL: Existing Journal Entry found.")
            else:
                 print("VERIFICATION FAILED: Existing Journal Entry not found.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    verify_integration()
