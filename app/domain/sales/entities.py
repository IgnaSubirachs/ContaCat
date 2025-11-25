from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional, List
from decimal import Decimal
from enum import Enum
import uuid


class QuoteStatus(Enum):
    """Status of a quote."""
    DRAFT = "DRAFT"  # Esborrany
    SENT = "SENT"  # Enviat
    ACCEPTED = "ACCEPTED"  # Acceptat
    REJECTED = "REJECTED"  # Rebutjat
    EXPIRED = "EXPIRED"  # Caducat


class OrderStatus(Enum):
    """Status of a sales order."""
    DRAFT = "DRAFT"  # Esborrany
    CONFIRMED = "CONFIRMED"  # Confirmat
    IN_PROGRESS = "IN_PROGRESS"  # En procés
    DELIVERED = "DELIVERED"  # Lliurat
    CANCELLED = "CANCELLED"  # Cancel·lat


class InvoiceStatus(Enum):
    """Status of a sales invoice."""
    DRAFT = "DRAFT"  # Esborrany
    POSTED = "POSTED"  # Comptabilitzat
    PAID = "PAID"  # Pagat
    CANCELLED = "CANCELLED"  # Cancel·lat


class PaymentStatus(Enum):
    """Payment status of an invoice."""
    PENDING = "PENDING"  # Pendent
    PARTIAL = "PARTIAL"  # Parcial
    PAID = "PAID"  # Pagat


@dataclass
class SalesLine:
    """Sales line entity (shared by Quote, Order, Invoice).
    
    Represents a line item in a sales document with product/service details,
    pricing, discounts, and tax calculations.
    """
    product_code: str  # Codi del producte/servei
    description: str  # Descripció
    quantity: Decimal  # Quantitat
    unit_price: Decimal  # Preu unitari
    discount_percent: Decimal = Decimal("0")  # Descompte (%)
    tax_rate: Decimal = Decimal("21")  # Tipus IVA (21, 10, 4, 0)
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        
        # Ensure Decimal types
        if not isinstance(self.quantity, Decimal):
            self.quantity = Decimal(str(self.quantity))
        if not isinstance(self.unit_price, Decimal):
            self.unit_price = Decimal(str(self.unit_price))
        if not isinstance(self.discount_percent, Decimal):
            self.discount_percent = Decimal(str(self.discount_percent))
        if not isinstance(self.tax_rate, Decimal):
            self.tax_rate = Decimal(str(self.tax_rate))
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate subtotal (quantity * unit_price)."""
        return (self.quantity * self.unit_price).quantize(Decimal("0.01"))
    
    @property
    def discount_amount(self) -> Decimal:
        """Calculate discount amount."""
        return (self.subtotal * self.discount_percent / 100).quantize(Decimal("0.01"))
    
    @property
    def subtotal_after_discount(self) -> Decimal:
        """Calculate subtotal after discount."""
        return (self.subtotal - self.discount_amount).quantize(Decimal("0.01"))
    
    @property
    def tax_amount(self) -> Decimal:
        """Calculate tax amount (IVA)."""
        return (self.subtotal_after_discount * self.tax_rate / 100).quantize(Decimal("0.01"))
    
    @property
    def total(self) -> Decimal:
        """Calculate total (subtotal after discount + tax)."""
        return (self.subtotal_after_discount + self.tax_amount).quantize(Decimal("0.01"))
    
    def validate(self) -> None:
        """Validate sales line."""
        if not self.product_code or not self.product_code.strip():
            raise ValueError("El codi del producte és obligatori")
        
        if not self.description or not self.description.strip():
            raise ValueError("La descripció és obligatòria")
        
        if self.quantity <= 0:
            raise ValueError("La quantitat ha de ser superior a 0")
        
        if self.unit_price < 0:
            raise ValueError("El preu unitari no pot ser negatiu")
        
        if self.discount_percent < 0 or self.discount_percent > 100:
            raise ValueError("El descompte ha d'estar entre 0 i 100")
        
        if self.tax_rate not in [Decimal("0"), Decimal("4"), Decimal("10"), Decimal("21")]:
            raise ValueError("El tipus d'IVA ha de ser 0, 4, 10 o 21")


@dataclass
class Quote:
    """Quote entity (Pressupost).
    
    Represents a customer quotation with lines, validity period, and status.
    Can be converted to a SalesOrder when accepted.
    """
    quote_number: str  # Número de pressupost
    quote_date: date  # Data del pressupost
    valid_until: date  # Vàlid fins
    partner_id: str  # ID del client
    lines: List[SalesLine] = field(default_factory=list)
    status: QuoteStatus = QuoteStatus.DRAFT
    notes: str = ""
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate total subtotal (sum of all lines)."""
        return sum(line.subtotal_after_discount for line in self.lines)
    
    @property
    def total_tax(self) -> Decimal:
        """Calculate total tax amount."""
        return sum(line.tax_amount for line in self.lines)
    
    @property
    def total(self) -> Decimal:
        """Calculate grand total."""
        return (self.subtotal + self.total_tax).quantize(Decimal("0.01"))
    
    @property
    def is_expired(self) -> bool:
        """Check if quote has expired."""
        return date.today() > self.valid_until
    
    def validate(self) -> None:
        """Validate quote."""
        if not self.quote_number or not self.quote_number.strip():
            raise ValueError("El número de pressupost és obligatori")
        
        if not self.partner_id or not self.partner_id.strip():
            raise ValueError("El client és obligatori")
        
        if not self.lines or len(self.lines) == 0:
            raise ValueError("El pressupost ha de tenir almenys una línia")
        
        if self.valid_until < self.quote_date:
            raise ValueError("La data de validesa no pot ser anterior a la data del pressupost")
        
        # Validate all lines
        for line in self.lines:
            line.validate()
    
    def send(self) -> None:
        """Mark quote as sent."""
        if self.status != QuoteStatus.DRAFT:
            raise ValueError("Només es poden enviar pressupostos en esborrany")
        self.validate()
        self.status = QuoteStatus.SENT
    
    def accept(self) -> None:
        """Accept quote."""
        if self.status not in [QuoteStatus.SENT, QuoteStatus.DRAFT]:
            raise ValueError("Només es poden acceptar pressupostos enviats o en esborrany")
        if self.is_expired:
            raise ValueError("No es pot acceptar un pressupost caducat")
        self.status = QuoteStatus.ACCEPTED
    
    def reject(self) -> None:
        """Reject quote."""
        if self.status not in [QuoteStatus.SENT, QuoteStatus.DRAFT]:
            raise ValueError("Només es poden rebutjar pressupostos enviats o en esborrany")
        self.status = QuoteStatus.REJECTED
    
    def can_edit(self) -> bool:
        """Check if quote can be edited."""
        return self.status == QuoteStatus.DRAFT


@dataclass
class SalesOrder:
    """Sales order entity (Comanda de venda).
    
    Represents a confirmed customer order with delivery details.
    Can be created from a Quote or standalone.
    Can be converted to a SalesInvoice.
    """
    order_number: str  # Número de comanda
    order_date: date  # Data de la comanda
    partner_id: str  # ID del client
    lines: List[SalesLine] = field(default_factory=list)
    status: OrderStatus = OrderStatus.DRAFT
    quote_id: Optional[str] = None  # Referència al pressupost
    delivery_date: Optional[date] = None  # Data de lliurament prevista
    delivery_address: str = ""  # Adreça de lliurament
    notes: str = ""
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate total subtotal."""
        return sum(line.subtotal_after_discount for line in self.lines)
    
    @property
    def total_tax(self) -> Decimal:
        """Calculate total tax amount."""
        return sum(line.tax_amount for line in self.lines)
    
    @property
    def total(self) -> Decimal:
        """Calculate grand total."""
        return (self.subtotal + self.total_tax).quantize(Decimal("0.01"))
    
    def validate(self) -> None:
        """Validate sales order."""
        if not self.order_number or not self.order_number.strip():
            raise ValueError("El número de comanda és obligatori")
        
        if not self.partner_id or not self.partner_id.strip():
            raise ValueError("El client és obligatori")
        
        if not self.lines or len(self.lines) == 0:
            raise ValueError("La comanda ha de tenir almenys una línia")
        
        if self.delivery_date and self.delivery_date < self.order_date:
            raise ValueError("La data de lliurament no pot ser anterior a la data de la comanda")
        
        # Validate all lines
        for line in self.lines:
            line.validate()
    
    def confirm(self) -> None:
        """Confirm order."""
        if self.status != OrderStatus.DRAFT:
            raise ValueError("Només es poden confirmar comandes en esborrany")
        self.validate()
        self.status = OrderStatus.CONFIRMED
    
    def start_progress(self) -> None:
        """Mark order as in progress."""
        if self.status != OrderStatus.CONFIRMED:
            raise ValueError("Només es poden processar comandes confirmades")
        self.status = OrderStatus.IN_PROGRESS
    
    def deliver(self) -> None:
        """Mark order as delivered."""
        if self.status not in [OrderStatus.CONFIRMED, OrderStatus.IN_PROGRESS]:
            raise ValueError("Només es poden lliurar comandes confirmades o en procés")
        self.status = OrderStatus.DELIVERED
    
    def cancel(self) -> None:
        """Cancel order."""
        if self.status == OrderStatus.DELIVERED:
            raise ValueError("No es pot cancel·lar una comanda ja lliurada")
        self.status = OrderStatus.CANCELLED
    
    def can_edit(self) -> bool:
        """Check if order can be edited."""
        return self.status == OrderStatus.DRAFT


@dataclass
class SalesInvoice:
    """Sales invoice entity (Factura de venda).
    
    Represents a customer invoice with automatic accounting integration.
    Format: {series}/{year}/{number} (e.g., A/2025/001)
    """
    series: str  # Sèrie de factura (A, B, C, etc.)
    year: int  # Any
    number: int  # Número seqüencial
    invoice_date: date  # Data de factura
    due_date: date  # Data de venciment
    partner_id: str  # ID del client
    lines: List[SalesLine] = field(default_factory=list)
    status: InvoiceStatus = InvoiceStatus.DRAFT
    payment_status: PaymentStatus = PaymentStatus.PENDING
    order_id: Optional[str] = None  # Referència a la comanda
    journal_entry_id: Optional[str] = None  # Referència a l'assentament comptable
    notes: str = ""
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
    
    @property
    def invoice_number(self) -> str:
        """Get formatted invoice number (A/2025/001)."""
        return f"{self.series}/{self.year}/{self.number:03d}"
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate total subtotal."""
        return sum(line.subtotal_after_discount for line in self.lines)
    
    @property
    def total_tax(self) -> Decimal:
        """Calculate total tax amount."""
        return sum(line.tax_amount for line in self.lines)
    
    @property
    def total(self) -> Decimal:
        """Calculate grand total."""
        return (self.subtotal + self.total_tax).quantize(Decimal("0.01"))
    
    @property
    def tax_breakdown(self) -> dict:
        """Get tax breakdown by rate."""
        breakdown = {}
        for line in self.lines:
            rate = float(line.tax_rate)
            if rate not in breakdown:
                breakdown[rate] = {
                    "base": Decimal("0"),
                    "tax": Decimal("0")
                }
            breakdown[rate]["base"] += line.subtotal_after_discount
            breakdown[rate]["tax"] += line.tax_amount
        return breakdown
    
    def validate(self) -> None:
        """Validate sales invoice."""
        if not self.series or not self.series.strip():
            raise ValueError("La sèrie de factura és obligatòria")
        
        if self.year < 2000 or self.year > 2100:
            raise ValueError("L'any de factura no és vàlid")
        
        if self.number <= 0:
            raise ValueError("El número de factura ha de ser superior a 0")
        
        if not self.partner_id or not self.partner_id.strip():
            raise ValueError("El client és obligatori")
        
        if not self.lines or len(self.lines) == 0:
            raise ValueError("La factura ha de tenir almenys una línia")
        
        if self.due_date < self.invoice_date:
            raise ValueError("La data de venciment no pot ser anterior a la data de factura")
        
        # Validate all lines
        for line in self.lines:
            line.validate()
    
    def post(self) -> None:
        """Post invoice (ready for accounting integration)."""
        if self.status != InvoiceStatus.DRAFT:
            raise ValueError("Només es poden comptabilitzar factures en esborrany")
        self.validate()
        self.status = InvoiceStatus.POSTED
    
    def mark_as_paid(self) -> None:
        """Mark invoice as paid."""
        if self.status != InvoiceStatus.POSTED:
            raise ValueError("Només es poden marcar com a pagades factures comptabilitzades")
        self.payment_status = PaymentStatus.PAID
        self.status = InvoiceStatus.PAID
    
    def can_edit(self) -> bool:
        """Check if invoice can be edited."""
        return self.status == InvoiceStatus.DRAFT
