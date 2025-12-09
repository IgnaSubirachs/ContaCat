from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.assets.entities import Asset, DepreciationEntry

class AssetRepository(ABC):
    @abstractmethod
    def save(self, asset: Asset) -> Asset:
        """Create or update an asset."""
        pass

    @abstractmethod
    def get_by_id(self, asset_id: int) -> Optional[Asset]:
        """Get asset by ID."""
        pass

    @abstractmethod
    def get_by_code(self, code: str) -> Optional[Asset]:
        """Get asset by code."""
        pass

    @abstractmethod
    def list_all(self) -> List[Asset]:
        """List all assets."""
        pass

    @abstractmethod
    def add_depreciation_entry(self, entry: DepreciationEntry) -> DepreciationEntry:
        """Add a depreciation entry to an asset."""
        pass
