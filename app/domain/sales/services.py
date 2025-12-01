from typing import List, Optional
from datetime import date, timedelta
from decimal import Decimal

from app.domain.sales.entities import (
    Quote, SalesOrder, SalesInvoice, SalesLine,
    QuoteStatus, OrderStatus, InvoiceStatus
)
from app.domain.sales.repositories import (
    QuoteRepository, SalesOrderRepository, SalesInvoiceRepository
)
from app.domain.partners.repositories import PartnerRepository
from app.domain.accounting.services import AccountingService


class QuoteService:
    """Service for managing quotes (pressupostos)."""
    
    def __init__(
        self,
        quote_repo: QuoteRepository,
        partner_repo: PartnerRepository
    ):
        self._quote_repo = quote_repo
        self._partner_repo = partner_repo
    
    def create_quote(
        self,
        partner_id: str,
        quote_date: date,
        valid_days: int = 30,
        lines: List[dict] = None,
        notes: str = ""
    ) -> Quote:
        """Create a new quote."""
        # Verify partner exists
        partner = self._partner_repo.find_by_id(partner_id)
        if not partner:
            raise ValueError(f"No s'ha trobat el client amb ID {partner_id}")
        
        if not partner.is_customer:
            raise ValueError("El partner ha de ser un client")
        
        # Get next quote number
        quote_number = self._quote_repo.get_next_quote_number()
        
        # Calculate valid_until
        valid_until = quote_date + timedelta(days=valid_days)
        
        # Create sales lines
        sales_lines = []
        if lines:
            for line_data in lines:
                line = SalesLine(
                    product_code=line_data["product_code"],
                    description=line_data["description"],
                    quantity=Decimal(str(line_data["quantity"])),
                    unit_price=Decimal(str(line_data["unit_price"])),
                    discount_percent=Decimal(str(line_data.get("discount_percent", 0))),
                    tax_rate=Decimal(str(line_data.get("tax_rate", 21)))
                )
                sales_lines.append(line)
        
        # Create quote
        quote = Quote(
            quote_number=quote_number,
            quote_date=quote_date,
            valid_until=valid_until,
            partner_id=partner_id,
            lines=sales_lines,
            notes=notes
        )
        
        quote.validate()
        self._quote_repo.add(quote)
        return quote
    
    def update_quote(
        self,
        quote_id: str,
        lines: List[dict] = None,
        notes: str = None
    ) -> Quote:
        """Update an existing quote (only drafts)."""
        quote = self._quote_repo.find_by_id(quote_id)
        if not quote:
            raise ValueError(f"No s'ha trobat el pressupost amb ID {quote_id}")
        
        if not quote.can_edit():
            raise ValueError("Només es poden editar pressupostos en esborrany")
        
        # Update lines if provided
        if lines is not None:
            sales_lines = []
            for line_data in lines:
                line = SalesLine(
                    product_code=line_data["product_code"],
                    description=line_data["description"],
                    quantity=Decimal(str(line_data["quantity"])),
                    unit_price=Decimal(str(line_data["unit_price"])),
                    discount_percent=Decimal(str(line_data.get("discount_percent", 0))),
                    tax_rate=Decimal(str(line_data.get("tax_rate", 21)))
                )
                sales_lines.append(line)
            quote.lines = sales_lines
        
        # Update notes if provided
        if notes is not None:
            quote.notes = notes
        
        quote.validate()
        self._quote_repo.update(quote)
        return quote
    
    def send_quote(self, quote_id: str) -> Quote:
        """Send a quote to customer."""
        quote = self._quote_repo.find_by_id(quote_id)
        if not quote:
            raise ValueError(f"No s'ha trobat el pressupost amb ID {quote_id}")
        
        quote.send()
        self._quote_repo.update(quote)
        return quote
    
    def accept_quote(self, quote_id: str) -> Quote:
        """Accept a quote."""
        quote = self._quote_repo.find_by_id(quote_id)
        if not quote:
            raise ValueError(f"No s'ha trobat el pressupost amb ID {quote_id}")
        
        quote.accept()
        self._quote_repo.update(quote)
        return quote
    
    def reject_quote(self, quote_id: str) -> Quote:
        """Reject a quote."""
        quote = self._quote_repo.find_by_id(quote_id)
        if not quote:
            raise ValueError(f"No s'ha trobat el pressupost amb ID {quote_id}")
        
        quote.reject()
        self._quote_repo.update(quote)
        return quote
    
    def get_quote(self, quote_id: str) -> Optional[Quote]:
        """Get quote by ID."""
        return self._quote_repo.find_by_id(quote_id)
    
    def list_quotes(self, partner_id: str = None, status: QuoteStatus = None) -> List[Quote]:
        """List quotes with optional filters."""
        if partner_id:
            return self._quote_repo.list_by_partner(partner_id)
        elif status:
            return self._quote_repo.list_by_status(status)
        else:
            return self._quote_repo.list_all()
    
    def delete_quote(self, quote_id: str) -> None:
        """Delete a quote (only drafts)."""
        quote = self._quote_repo.find_by_id(quote_id)
        if not quote:
            raise ValueError(f"No s'ha trobat el pressupost amb ID {quote_id}")
        
        if not quote.can_edit():
            raise ValueError("Només es poden eliminar pressupostos en esborrany")
        
        self._quote_repo.delete(quote_id)


class SalesOrderService:
    """Service for managing sales orders (comandes)."""
    
    def __init__(
        self,
        order_repo: SalesOrderRepository,
        quote_repo: QuoteRepository,
        partner_repo: PartnerRepository
    ):
        self._order_repo = order_repo
        self._quote_repo = quote_repo
        self._partner_repo = partner_repo
    
    def create_order(
        self,
        partner_id: str,
        order_date: date,
        lines: List[dict],
        delivery_date: Optional[date] = None,
        delivery_address: str = "",
        notes: str = ""
    ) -> SalesOrder:
        """Create a new sales order."""
        # Verify partner exists
        partner = self._partner_repo.find_by_id(partner_id)
        if not partner:
            raise ValueError(f"No s'ha trobat el client amb ID {partner_id}")
        
        if not partner.is_customer:
            raise ValueError("El partner ha de ser un client")
        
        # Get next order number
        order_number = self._order_repo.get_next_order_number()
        
        # Create sales lines
        sales_lines = []
        for line_data in lines:
            line = SalesLine(
                product_code=line_data["product_code"],
                description=line_data["description"],
                quantity=Decimal(str(line_data["quantity"])),
                unit_price=Decimal(str(line_data["unit_price"])),
                discount_percent=Decimal(str(line_data.get("discount_percent", 0))),
                tax_rate=Decimal(str(line_data.get("tax_rate", 21)))
            )
            sales_lines.append(line)
        
        # Create order
        order = SalesOrder(
            order_number=order_number,
            order_date=order_date,
            partner_id=partner_id,
            lines=sales_lines,
            delivery_date=delivery_date,
            delivery_address=delivery_address,
            notes=notes
        )
        
        order.validate()
        self._order_repo.add(order)
        return order
    
    def create_from_quote(self, quote_id: str, order_date: date = None) -> SalesOrder:
        """Create a sales order from an accepted quote."""
        quote = self._quote_repo.find_by_id(quote_id)
        if not quote:
            raise ValueError(f"No s'ha trobat el pressupost amb ID {quote_id}")
        
        if quote.status != QuoteStatus.ACCEPTED:
            raise ValueError("Només es poden convertir pressupostos acceptats")
        
        # Get next order number
        order_number = self._order_repo.get_next_order_number()
        
        # Use today if no date provided
        if order_date is None:
            order_date = date.today()
        
        # Copy lines from quote
        order_lines = [
            SalesLine(
                product_code=line.product_code,
                description=line.description,
                quantity=line.quantity,
                unit_price=line.unit_price,
                discount_percent=line.discount_percent,
                tax_rate=line.tax_rate
            )
            for line in quote.lines
        ]
        
        # Create order
        order = SalesOrder(
            order_number=order_number,
            order_date=order_date,
            partner_id=quote.partner_id,
            lines=order_lines,
            quote_id=quote_id,
            notes=quote.notes
        )
        
        order.validate()
        self._order_repo.add(order)
        return order
    
    def confirm_order(self, order_id: str) -> SalesOrder:
        """Confirm a sales order."""
        order = self._order_repo.find_by_id(order_id)
        if not order:
            raise ValueError(f"No s'ha trobat la comanda amb ID {order_id}")
        
        order.confirm()
        self._order_repo.update(order)
        return order
    
    def deliver_order(self, order_id: str) -> SalesOrder:
        """Mark order as delivered."""
        order = self._order_repo.find_by_id(order_id)
        if not order:
            raise ValueError(f"No s'ha trobat la comanda amb ID {order_id}")
        
        order.deliver()
        self._order_repo.update(order)
        return order
    
    def cancel_order(self, order_id: str) -> SalesOrder:
        """Cancel a sales order."""
        order = self._order_repo.find_by_id(order_id)
        if not order:
            raise ValueError(f"No s'ha trobat la comanda amb ID {order_id}")
        
        order.cancel()
        self._order_repo.update(order)
        return order
    
    def get_order(self, order_id: str) -> Optional[SalesOrder]:
        """Get order by ID."""
        return self._order_repo.find_by_id(order_id)
    
    def list_orders(self, partner_id: str = None, status: OrderStatus = None) -> List[SalesOrder]:
        """List orders with optional filters."""
        if partner_id:
            return self._order_repo.list_by_partner(partner_id)
        elif status:
            return self._order_repo.list_by_status(status)
        else:
            return self._order_repo.list_all()


class SalesInvoiceService:
    """Service for managing sales invoices (factures)."""
    
    def __init__(
        self,
        invoice_repo: SalesInvoiceRepository,
        order_repo: SalesOrderRepository,
        partner_repo: PartnerRepository,
        accounting_service: AccountingService
    ):
        self._invoice_repo = invoice_repo
        self._order_repo = order_repo
        self._partner_repo = partner_repo
        self._accounting_service = accounting_service
    
    def create_invoice(
        self,
        partner_id: str,
        invoice_date: date,
        lines: List[dict],
        series: str = "A",
        payment_days: int = 30,
        notes: str = ""
    ) -> SalesInvoice:
        """Create a new sales invoice."""
        # Verify partner exists
        partner = self._partner_repo.find_by_id(partner_id)
        if not partner:
            raise ValueError(f"No s'ha trobat el client amb ID {partner_id}")
        
        if not partner.is_customer:
            raise ValueError("El partner ha de ser un client")
        
        # Get next invoice number
        year = invoice_date.year
        number = self._invoice_repo.get_next_invoice_number(series, year)
        
        # Calculate due date
        due_date = invoice_date + timedelta(days=payment_days)
        
        # Create sales lines
        sales_lines = []
        for line_data in lines:
            line = SalesLine(
                product_code=line_data["product_code"],
                description=line_data["description"],
                quantity=Decimal(str(line_data["quantity"])),
                unit_price=Decimal(str(line_data["unit_price"])),
                discount_percent=Decimal(str(line_data.get("discount_percent", 0))),
                tax_rate=Decimal(str(line_data.get("tax_rate", 21)))
            )
            sales_lines.append(line)
        
        # Create invoice
        invoice = SalesInvoice(
            series=series,
            year=year,
            number=number,
            invoice_date=invoice_date,
            due_date=due_date,
            partner_id=partner_id,
            lines=sales_lines,
            notes=notes
        )
        
        invoice.validate()
        self._invoice_repo.add(invoice)
        return invoice
    
    def create_from_order(self, order_id: str, invoice_date: date = None, series: str = "A") -> SalesInvoice:
        """Create a sales invoice from a delivered order."""
        order = self._order_repo.find_by_id(order_id)
        if not order:
            raise ValueError(f"No s'ha trobat la comanda amb ID {order_id}")
        
        if order.status != OrderStatus.DELIVERED:
            raise ValueError("Només es poden facturar comandes lliurades")
        
        # Use today if no date provided
        if invoice_date is None:
            invoice_date = date.today()
        
        # Get partner for payment terms
        partner = self._partner_repo.find_by_id(order.partner_id)
        payment_days = partner.payment_days if partner else 30
        
        # Get next invoice number
        year = invoice_date.year
        number = self._invoice_repo.get_next_invoice_number(series, year)
        
        # Calculate due date
        due_date = invoice_date + timedelta(days=payment_days)
        
        # Copy lines from order
        invoice_lines = [
            SalesLine(
                product_code=line.product_code,
                description=line.description,
                quantity=line.quantity,
                unit_price=line.unit_price,
                discount_percent=line.discount_percent,
                tax_rate=line.tax_rate
            )
            for line in order.lines
        ]
        
        # Create invoice
        invoice = SalesInvoice(
            series=series,
            year=year,
            number=number,
            invoice_date=invoice_date,
            due_date=due_date,
            partner_id=order.partner_id,
            lines=invoice_lines,
            order_id=order_id,
            notes=order.notes
        )
        
        invoice.validate()
        self._invoice_repo.add(invoice)
        return invoice
    
    def post_invoice(self, invoice_id: str) -> SalesInvoice:
        """Post invoice and create accounting journal entry."""
        invoice = self._invoice_repo.find_by_id(invoice_id)
        if not invoice:
            raise ValueError(f"No s'ha trobat la factura amb ID {invoice_id}")
        
        # Post invoice
        invoice.post()
        
        # Create journal entry
        # Debit: Customer account (430)
        # Credit: Sales account (700)
        # Credit: VAT account (477)
        
        journal_lines = []
        
        # Debit: Customer account (total)
        # Using standard customer receivables account
        journal_lines.append((
            "43000000",  # Customer receivables account
            invoice.total,
            Decimal("0"),
            f"Factura {invoice.invoice_number}"
        ))
        
        # Credit: Sales account (subtotal)
        journal_lines.append((
            "70000000",  # Sales revenue account
            Decimal("0"),
            invoice.subtotal,
            f"Venda factura {invoice.invoice_number}"
        ))
        
        # Credit: VAT accounts (by tax rate)
        tax_breakdown = invoice.tax_breakdown
        for rate, amounts in tax_breakdown.items():
            if amounts["tax"] > 0:
                journal_lines.append((
                    "47700000",  # VAT payable account
                    Decimal("0"),
                    amounts["tax"],
                    f"IVA {rate}% factura {invoice.invoice_number}"
                ))
        
        # Create journal entry
        journal_entry = self._accounting_service.create_journal_entry(
            entry_date=invoice.invoice_date,
            description=f"Factura de venda {invoice.invoice_number}",
            lines=journal_lines
        )
        
        # Auto-post the journal entry
        self._accounting_service.post_journal_entry(journal_entry.id)
        
        # Link journal entry to invoice
        invoice.journal_entry_id = journal_entry.id
        self._invoice_repo.update(invoice)
        
        return invoice
    
    def mark_as_paid(self, invoice_id: str) -> SalesInvoice:
        """Mark invoice as paid."""
        invoice = self._invoice_repo.find_by_id(invoice_id)
        if not invoice:
            raise ValueError(f"No s'ha trobat la factura amb ID {invoice_id}")
        
        invoice.mark_as_paid()
        self._invoice_repo.update(invoice)
        return invoice
    
    def get_invoice(self, invoice_id: str) -> Optional[SalesInvoice]:
        """Get invoice by ID."""
        return self._invoice_repo.find_by_id(invoice_id)
    
    def list_invoices(self, partner_id: str = None, status: InvoiceStatus = None) -> List[SalesInvoice]:
        """List invoices with optional filters."""
        if partner_id:
            return self._invoice_repo.list_by_partner(partner_id)
        elif status:
            return self._invoice_repo.list_by_status(status)
        else:
            return self._invoice_repo.list_all()
