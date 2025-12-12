from sqlalchemy import Column, Integer, String, Float, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
from app.domain.assets.entities import AssetStatus, DepreciationMethod

class AssetModel(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    
    purchase_date = Column(Date, nullable=False)
    purchase_price = Column(Float, nullable=False)
    
    useful_life_years = Column(Integer, nullable=False)
    residual_value = Column(Float, default=0.0)
    
    depreciation_method = Column(Enum(DepreciationMethod), default=DepreciationMethod.LINEAR)
    status = Column(Enum(AssetStatus), default=AssetStatus.ACTIVE)
    
    account_code_asset = Column(String(20), nullable=False)
    account_code_accumulated_depreciation = Column(String(20), nullable=False)
    account_code_depreciation_expense = Column(String(20), nullable=False)
    
    depreciation_entries = relationship("DepreciationEntryModel", back_populates="asset", cascade="all, delete-orphan")

class DepreciationEntryModel(Base):
    __tablename__ = "depreciation_entries"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    accumulated_depreciation = Column(Float, nullable=False)
    description = Column(String(255), nullable=False)
    journal_entry_id = Column(Integer, nullable=True) # Link to accounting journal entry
    
    asset = relationship("AssetModel", back_populates="depreciation_entries")
