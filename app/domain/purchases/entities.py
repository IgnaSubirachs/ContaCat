"""Purchase domain entities."""
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import List, Optional
import uuid


class PurchaseOrderStatus(str, Enum):
    """Purchase order status."""
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    RECEIVED = "RECEIVED"
    INVOICED = "INVOICED"
    CANCELLED = "CANCELLED"


class PurchaseInvoiceStatus(str, Enum):
    """Purchase invoice status."""
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class PaymentStatus(str, Enum):
    """Payment status."""
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    PAID = "PAID"


@dataclass
class PurchaseOrderLine:
    """Purchase order line item."""
    description: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal = Decimal("21.00")
    product_id: Optional[str] = None
    line_number: int = 1
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @property
    def tax_amount(self) -> Decimal:
        """Calculate tax amount."""
        subtotal = self.quantity * self.unit_price
        return subtotal * (self.tax_rate / Decimal("100"))
    
    @property
    def total(self) -> Decimal:
        """Calculate line total with tax."""
        subtotal = self.quantity * self.unit_price
        return subtotal + self.tax_amount


@dataclass
class PurchaseOrder:
    """Purchase order entity."""
    partner_id: str
    order_date: date
    lines: List[PurchaseOrderLine]
    order_number: str = ""
    status: PurchaseOrderStatus = PurchaseOrderStatus.DRAFT
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate order subtotal (before tax)."""
        return sum(line.quantity * line.unit_price for line in self.lines)
    
    @property
    def tax_amount(self) -> Decimal:
        """Calculate total tax amount."""
        return sum(line.tax_amount for line in self.lines)
    
    @property
    def total_amount(self) -> Decimal:
        """Calculate total amount including tax."""
        return self.subtotal + self.tax_amount


@dataclass
class PurchaseInvoiceLine:
    """Purchase invoice line item."""
    description: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal = Decimal("21.00")
    product_id: Optional[str] = None
    line_number: int = 1
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @property
    def tax_amount(self) -> Decimal:
        """Calculate tax amount."""
        subtotal = self.quantity * self.unit_price
        return subtotal * (self.tax_rate / Decimal("100"))
    
    @property
    def total(self) -> Decimal:
        """Calculate line total with tax."""
        subtotal = self.quantity * self.unit_price
        return subtotal + self.tax_amount


@dataclass
class PurchaseInvoice:
    """Purchase invoice entity."""
    partner_id: str
    invoice_date: date
    lines: List[PurchaseInvoiceLine]
    invoice_number: str = ""
    supplier_reference: str = ""  # Supplier's invoice number
    due_date: Optional[date] = None
    purchase_order_id: Optional[str] = None
    status: PurchaseInvoiceStatus = PurchaseInvoiceStatus.DRAFT
    payment_status: PaymentStatus = PaymentStatus.PENDING
    amount_paid: Decimal = Decimal("0")
    journal_entry_id: Optional[str] = None
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate invoice subtotal (before tax)."""
        return sum(line.quantity * line.unit_price for line in self.lines)
    
    @property
    def tax_amount(self) -> Decimal:
        """Calculate total tax amount."""
        return sum(line.tax_amount for line in self.lines)
    
    @property
    def total_amount(self) -> Decimal:
        """Calculate total amount including tax."""
        return self.subtotal + self.tax_amount
    
    @property
    def amount_due(self) -> Decimal:
        """Calculate remaining amount due."""
        return self.total_amount - self.amount_paid
