import sys
import os
from datetime import date

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infrastructure.db.base import SessionLocal, init_db
from app.domain.assets.entities import Asset, AssetStatus, DepreciationMethod
from app.infrastructure.persistence.assets.repositories import SqlAlchemyAssetRepository
from app.domain.assets.services import AssetService

def verify_assets():
    print("Initializing database...")
    init_db()
    db = SessionLocal()
    
    try:
        repo = SqlAlchemyAssetRepository(db)
        service = AssetService(repo)
        
        # 1. Create Asset
        print("\n1. Creating Test Asset...")
        asset_code = "TEST-ASSET-001"
        
        # Check if exists and delete if so (for re-runability)
        existing = repo.get_by_code(asset_code)
        if existing:
            print(f"Asset {asset_code} already exists. Skipping creation.")
            asset = existing
        else:
            new_asset = Asset(
                code=asset_code,
                name="Test Laptop",
                description="High-end laptop for development",
                purchase_date=date(2024, 1, 1),
                purchase_price=2000.0,
                useful_life_years=4,
                residual_value=0.0,
                depreciation_method=DepreciationMethod.LINEAR,
                status=AssetStatus.ACTIVE,
                account_code_asset="217000",
                account_code_accumulated_depreciation="281700",
                account_code_depreciation_expense="681700"
            )
            asset = service.create_asset(new_asset)
            print(f"Asset created: {asset.name} (ID: {asset.id})")

        # 2. Verify Depreciation Calculation
        print("\n2. Verifying Depreciation Calculation...")
        annual_depreciation = service.calculate_annual_depreciation(asset)
        expected_annual = 2000.0 / 4
        print(f"Annual Depreciation: {annual_depreciation} (Expected: {expected_annual})")
        
        if abs(annual_depreciation - expected_annual) > 0.01:
            print("ERROR: Depreciation calculation incorrect!")
            return

        # 3. Generate Depreciation Entry
        print("\n3. Generating Depreciation Entry for 2024...")
        try:
            entry = service.generate_depreciation_entries(asset.id, 2024)
            print(f"Entry generated: {entry.amount}€ on {entry.date}")
            print(f"Accumulated Depreciation: {entry.accumulated_depreciation}€")
        except ValueError as e:
            print(f"Depreciation generation failed (might be already done): {e}")

        # 4. Verify Persistence
        print("\n4. Verifying Persistence...")
        refreshed_asset = service.get_asset(asset.id)
        print(f"Asset Current Value: {refreshed_asset.current_value}€")
        print(f"Asset Status: {refreshed_asset.status}")
        
        if len(refreshed_asset.depreciation_entries) > 0:
            print("SUCCESS: Depreciation entries found.")
        else:
            print("ERROR: No depreciation entries found.")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_assets()
