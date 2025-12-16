"""Purchase repositories (abstract interfaces)."""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.purchases.entities import (
    PurchaseOrder,
    PurchaseInvoice,
    PurchaseOrderStatus,
    PurchaseInvoiceStatus
)


class PurchaseOrderRepository(ABC):
    """Abstract repository for purchase orders."""
    
    @abstractmethod
    def save(self, order: PurchaseOrder) -> PurchaseOrder:
        """Save or update a purchase order."""
        pass
    
    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[PurchaseOrder]:
        """Find purchase order by ID."""
        pass
    
    @abstractmethod
    def list_all(self) -> List[PurchaseOrder]:
        """List all purchase orders."""
        pass
    
    @abstractmethod
    def list_by_status(self, status: PurchaseOrderStatus) -> List[PurchaseOrder]:
        """List orders by status."""
        pass
    
    @abstractmethod
    def list_by_partner(self, partner_id: str) -> List[PurchaseOrder]:
        """List orders by supplier."""
        pass
    
    @abstractmethod
    def delete(self, order_id: str) -> bool:
        """Delete a purchase order."""
        pass
    
    @abstractmethod
    def get_next_order_number(self) -> str:
        """Generate next order number."""
        pass


class PurchaseInvoiceRepository(ABC):
    """Abstract repository for purchase invoices."""
    
    @abstractmethod
    def save(self, invoice: PurchaseInvoice) -> PurchaseInvoice:
        """Save or update a purchase invoice."""
        pass
    
    @abstractmethod
    def find_by_id(self, invoice_id: str) -> Optional[PurchaseInvoice]:
        """Find purchase invoice by ID."""
        pass
    
    @abstractmethod
    def list_all(self) -> List[PurchaseInvoice]:
        """List all purchase invoices."""
        pass
    
    @abstractmethod
    def list_by_status(self, status: PurchaseInvoiceStatus) -> List[PurchaseInvoice]:
        """List invoices by status."""
        pass
    
    @abstractmethod
    def list_by_partner(self, partner_id: str) -> List[PurchaseInvoice]:
        """List invoices by supplier."""
        pass
    
    @abstractmethod
    def delete(self, invoice_id: str) -> bool:
        """Delete a purchase invoice."""
        pass
    
    @abstractmethod
    def get_next_invoice_number(self) -> str:
        """Generate next invoice number."""
        pass
