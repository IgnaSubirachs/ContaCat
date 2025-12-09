from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.assets.entities import Asset, DepreciationEntry
from app.domain.assets.repositories import AssetRepository
from app.infrastructure.persistence.assets.models import AssetModel, DepreciationEntryModel

class SqlAlchemyAssetRepository(AssetRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: AssetModel) -> Asset:
        if not model:
            return None
        
        entries = [
            DepreciationEntry(
                id=entry.id,
                asset_id=entry.asset_id,
                date=entry.date,
                amount=entry.amount,
                accumulated_depreciation=entry.accumulated_depreciation,
                description=entry.description,
                journal_entry_id=entry.journal_entry_id
            ) for entry in model.depreciation_entries
        ]
        
        return Asset(
            id=model.id,
            code=model.code,
            name=model.name,
            description=model.description,
            purchase_date=model.purchase_date,
            purchase_price=model.purchase_price,
            useful_life_years=model.useful_life_years,
            residual_value=model.residual_value,
            depreciation_method=model.depreciation_method,
            status=model.status,
            account_code_asset=model.account_code_asset,
            account_code_accumulated_depreciation=model.account_code_accumulated_depreciation,
            account_code_depreciation_expense=model.account_code_depreciation_expense,
            depreciation_entries=entries
        )

    def save(self, asset: Asset) -> Asset:
        if asset.id:
            model = self.db.query(AssetModel).filter(AssetModel.id == asset.id).first()
            if model:
                model.code = asset.code
                model.name = asset.name
                model.description = asset.description
                model.purchase_date = asset.purchase_date
                model.purchase_price = asset.purchase_price
                model.useful_life_years = asset.useful_life_years
                model.residual_value = asset.residual_value
                model.depreciation_method = asset.depreciation_method
                model.status = asset.status
                model.account_code_asset = asset.account_code_asset
                model.account_code_accumulated_depreciation = asset.account_code_accumulated_depreciation
                model.account_code_depreciation_expense = asset.account_code_depreciation_expense
        else:
            model = AssetModel(
                code=asset.code,
                name=asset.name,
                description=asset.description,
                purchase_date=asset.purchase_date,
                purchase_price=asset.purchase_price,
                useful_life_years=asset.useful_life_years,
                residual_value=asset.residual_value,
                depreciation_method=asset.depreciation_method,
                status=asset.status,
                account_code_asset=asset.account_code_asset,
                account_code_accumulated_depreciation=asset.account_code_accumulated_depreciation,
                account_code_depreciation_expense=asset.account_code_depreciation_expense
            )
            self.db.add(model)
        
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, asset_id: int) -> Optional[Asset]:
        model = self.db.query(AssetModel).filter(AssetModel.id == asset_id).first()
        return self._to_entity(model)

    def get_by_code(self, code: str) -> Optional[Asset]:
        model = self.db.query(AssetModel).filter(AssetModel.code == code).first()
        return self._to_entity(model)

    def list_all(self) -> List[Asset]:
        models = self.db.query(AssetModel).all()
        return [self._to_entity(m) for m in models]

    def add_depreciation_entry(self, entry: DepreciationEntry) -> DepreciationEntry:
        model = DepreciationEntryModel(
            asset_id=entry.asset_id,
            date=entry.date,
            amount=entry.amount,
            accumulated_depreciation=entry.accumulated_depreciation,
            description=entry.description,
            journal_entry_id=entry.journal_entry_id
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        
        entry.id = model.id
        return entry
