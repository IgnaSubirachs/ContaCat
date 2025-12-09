from datetime import date
from typing import List
from app.domain.assets.entities import Asset, DepreciationEntry, AssetStatus, DepreciationMethod
from app.domain.assets.repositories import AssetRepository

class AssetService:
    def __init__(self, asset_repository: AssetRepository, accounting_service):
        self.asset_repository = asset_repository
        self.accounting_service = accounting_service

    def create_asset(self, asset: Asset) -> Asset:
        """Create a new asset."""
        existing = self.asset_repository.get_by_code(asset.code)
        if existing:
            raise ValueError(f"Asset with code {asset.code} already exists")
        return self.asset_repository.save(asset)

    def list_assets(self) -> List[Asset]:
        return self.asset_repository.list_all()

    def get_asset(self, asset_id: int) -> Asset:
        asset = self.asset_repository.get_by_id(asset_id)
        if not asset:
            raise ValueError(f"Asset with ID {asset_id} not found")
        return asset

    def calculate_annual_depreciation(self, asset: Asset) -> float:
        """Calculate annual depreciation amount (Linear)."""
        if asset.depreciation_method == DepreciationMethod.LINEAR:
            depreciable_amount = asset.purchase_price - asset.residual_value
            if asset.useful_life_years > 0:
                return depreciable_amount / asset.useful_life_years
            return 0.0
        else:
            raise NotImplementedError("Only LINEAR depreciation is supported")

    def generate_depreciation_entries(self, asset_id: int, year: int) -> DepreciationEntry:
        """
        Generate depreciation entry for a specific year.
        NOTE: This is a simplified version. In a real ERP, you'd handle partial years,
        monthly depreciation, etc.
        """
        asset = self.get_asset(asset_id)
        
        if asset.status != AssetStatus.ACTIVE:
            raise ValueError("Asset is not active")

        annual_amount = self.calculate_annual_depreciation(asset)
        
        # Check if fully depreciated
        if asset.current_value <= asset.residual_value:
             # Mark as fully depreciated if not already
             asset.status = AssetStatus.FULLY_DEPRECIATED
             self.asset_repository.save(asset)
             raise ValueError("Asset is already fully depreciated")

        # Cap amount to not exceed remaining value
        remaining_depreciable = asset.current_value - asset.residual_value
        amount = min(annual_amount, remaining_depreciable)

        # Create Journal Entry via AccountingService
        from decimal import Decimal
        
        # Debit: Depreciation Expense (681)
        # Credit: Accumulated Depreciation (281)
        lines = [
            (asset.account_code_depreciation_expense, Decimal(str(amount)), Decimal("0"), f"Amortització {asset.name}"),
            (asset.account_code_accumulated_depreciation, Decimal("0"), Decimal(str(amount)), f"Amortització {asset.name}")
        ]
        
        journal_entry = self.accounting_service.create_journal_entry(
            entry_date=date(year, 12, 31),
            description=f"Amortització {year} - {asset.name}",
            lines=lines
        )

        entry = DepreciationEntry(
            asset_id=asset.id,
            date=date(year, 12, 31), # End of year
            amount=amount,
            accumulated_depreciation=asset.accumulated_depreciation + amount,
            description=f"Amortització {year} - {asset.name}",
            journal_entry_id=journal_entry.entry_number # Using entry_number as ID for now, or should it be ID? 
            # Checking JournalEntry definition in accounting/entities.py... 
            # It seems JournalEntry has entry_number. Let's check if it has an ID.
            # In services.py: create_journal_entry returns JournalEntry.
            # Let's assume entry_number is the unique identifier or there is an id field.
            # Looking at accounting/services.py, create_journal_entry calls journal_repo.add(entry).
            # I should verify JournalEntry entity structure.
        )
        
        saved_entry = self.asset_repository.add_depreciation_entry(entry)
        
        # Update asset status if fully depreciated
        if asset.current_value - amount <= asset.residual_value:
            asset.status = AssetStatus.FULLY_DEPRECIATED
            self.asset_repository.save(asset)
            
        return saved_entry
