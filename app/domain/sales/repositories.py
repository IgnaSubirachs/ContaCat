from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.sales.entities import Quote, SalesOrder, SalesInvoice, QuoteStatus, OrderStatus, InvoiceStatus


class QuoteRepository(ABC):
    """Repository interface for Quote entity."""
    
    @abstractmethod
    def add(self, quote: Quote) -> None:
        """Add a new quote."""
        pass
    
    @abstractmethod
    def update(self, quote: Quote) -> None:
        """Update an existing quote."""
        pass
    
    @abstractmethod
    def delete(self, quote_id: str) -> None:
        """Delete a quote."""
        pass
    
    @abstractmethod
    def find_by_id(self, quote_id: str) -> Optional[Quote]:
        """Find quote by ID."""
        pass
    
    @abstractmethod
    def find_by_number(self, quote_number: str) -> Optional[Quote]:
        """Find quote by number."""
        pass
    
    @abstractmethod
    def list_all(self) -> List[Quote]:
        """List all quotes."""
        pass
    
    @abstractmethod
    def list_by_partner(self, partner_id: str) -> List[Quote]:
        """List quotes by partner."""
        pass
    
    @abstractmethod
    def list_by_status(self, status: QuoteStatus) -> List[Quote]:
        """List quotes by status."""
        pass
    
    @abstractmethod
    def get_next_quote_number(self) -> str:
        """Get next quote number."""
        pass


class SalesOrderRepository(ABC):
    """Repository interface for SalesOrder entity."""
    
    @abstractmethod
    def add(self, order: SalesOrder) -> None:
        """Add a new sales order."""
        pass
    
    @abstractmethod
    def update(self, order: SalesOrder) -> None:
        """Update an existing sales order."""
        pass
    
    @abstractmethod
    def delete(self, order_id: str) -> None:
        """Delete a sales order."""
        pass
    
    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[SalesOrder]:
        """Find sales order by ID."""
        pass
    
    @abstractmethod
    def find_by_number(self, order_number: str) -> Optional[SalesOrder]:
        """Find sales order by number."""
        pass
    
    @abstractmethod
    def list_all(self) -> List[SalesOrder]:
        """List all sales orders."""
        pass
    
    @abstractmethod
    def list_by_partner(self, partner_id: str) -> List[SalesOrder]:
        """List sales orders by partner."""
        pass
    
    @abstractmethod
    def list_by_status(self, status: OrderStatus) -> List[SalesOrder]:
        """List sales orders by status."""
        pass
    
    @abstractmethod
    def get_next_order_number(self) -> str:
        """Get next order number."""
        pass


class SalesInvoiceRepository(ABC):
    """Repository interface for SalesInvoice entity."""
    
    @abstractmethod
    def add(self, invoice: SalesInvoice) -> None:
        """Add a new sales invoice."""
        pass
    
    @abstractmethod
    def update(self, invoice: SalesInvoice) -> None:
        """Update an existing sales invoice."""
        pass
    
    @abstractmethod
    def delete(self, invoice_id: str) -> None:
        """Delete a sales invoice."""
        pass
    
    @abstractmethod
    def find_by_id(self, invoice_id: str) -> Optional[SalesInvoice]:
        """Find sales invoice by ID."""
        pass
    
    @abstractmethod
    def find_by_number(self, series: str, year: int, number: int) -> Optional[SalesInvoice]:
        """Find sales invoice by series, year, and number."""
        pass
    
    @abstractmethod
    def list_all(self) -> List[SalesInvoice]:
        """List all sales invoices."""
        pass
    
    @abstractmethod
    def list_by_partner(self, partner_id: str) -> List[SalesInvoice]:
        """List sales invoices by partner."""
        pass
    
    @abstractmethod
    def list_by_status(self, status: InvoiceStatus) -> List[SalesInvoice]:
        """List sales invoices by status."""
        pass
    
    @abstractmethod
    def get_next_invoice_number(self, series: str, year: int) -> int:
        """Get next invoice number for a series and year."""
        pass
