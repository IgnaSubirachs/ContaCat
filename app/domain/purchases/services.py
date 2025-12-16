"""Purchase services with business logic."""
import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional

from app.domain.purchases.entities import (
    PurchaseOrder,
    PurchaseOrderLine,
    PurchaseInvoice,
    PurchaseInvoiceLine,
    PurchaseOrderStatus,
    PurchaseInvoiceStatus,
    PaymentStatus
)
from app.domain.purchases.repositories import (
    PurchaseOrderRepository,
    PurchaseInvoiceRepository
)

logger = logging.getLogger(__name__)


class PurchaseOrderService:
    """Service for managing purchase orders."""
    
    def __init__(
        self,
        order_repo: PurchaseOrderRepository,
        partner_repo,
        inventory_service=None
    ):
        self._repo = order_repo
        self._partner_repo = partner_repo
        self._inventory = inventory_service
    
    def create_order(
        self,
        partner_id: str,
        lines: List[PurchaseOrderLine],
        order_date: Optional[date] = None,
        notes: str = ""
    ) -> PurchaseOrder:
        """Create a new purchase order."""
        if not order_date:
            order_date = date.today()
        
        # Generate order number
        order_number = self._repo.get_next_order_number()
        
        order = PurchaseOrder(
            order_number=order_number,
            partner_id=partner_id,
            order_date=order_date,
            lines=lines,
            status=PurchaseOrderStatus.DRAFT,
            notes=notes
        )
        
        return self._repo.save(order)
    
    def get_order(self, order_id: str) -> Optional[PurchaseOrder]:
        """Get purchase order by ID."""
        return self._repo.find_by_id(order_id)
    
    def list_orders(
        self,
        status: Optional[PurchaseOrderStatus] = None,
        partner_id: Optional[str] = None
    ) -> List[PurchaseOrder]:
        """List purchase orders."""
        if status:
            return self._repo.list_by_status(status)
        elif partner_id:
            return self._repo.list_by_partner(partner_id)
        return self._repo.list_all()
    
    def confirm_order(self, order_id: str) -> PurchaseOrder:
        """Confirm a draft purchase order."""
        order = self._repo.find_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        if order.status != PurchaseOrderStatus.DRAFT:
            raise ValueError("Only draft orders can be confirmed")
        
        order.status = PurchaseOrderStatus.CONFIRMED
        return self._repo.save(order)
    
    def receive_order(self, order_id: str) -> PurchaseOrder:
        """Mark order as received and update inventory."""
        order = self._repo.find_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        if order.status != PurchaseOrderStatus.CONFIRMED:
            raise ValueError("Only confirmed orders can be received")
        
        # Update inventory
        if self._inventory:
            for line in order.lines:
                if line.product_id:
                    try:
                        self._inventory.record_purchase(
                            product_id=line.product_id,
                            quantity=line.quantity,
                            reference=f"PO-{order.order_number}"
                        )
                    except Exception as e:
                        logger.warning(f"Inventory update failed: {e}")
        
        order.status = PurchaseOrderStatus.RECEIVED
        return self._repo.save(order)
    
    def cancel_order(self, order_id: str) -> PurchaseOrder:
        """Cancel a purchase order."""
        order = self._repo.find_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        if order.status in [PurchaseOrderStatus.RECEIVED, PurchaseOrderStatus.INVOICED]:
            raise ValueError("Cannot cancel received/invoiced orders")
        
        order.status = PurchaseOrderStatus.CANCELLED
        return self._repo.save(order)


class PurchaseInvoiceService:
    """Service for managing purchase invoices."""
    
    def __init__(
        self,
        invoice_repo: PurchaseInvoiceRepository,
        order_repo: PurchaseOrderRepository,
        partner_repo,
        accounting_service,
        mapping_service,
        audit_service=None,
        inventory_service=None
    ):
        self._repo = invoice_repo
        self._order_repo = order_repo
        self._partner_repo = partner_repo
        self._accounting = accounting_service
        self._mapping = mapping_service
        self._audit = audit_service
        self._inventory = inventory_service
    
    def create_invoice(
        self,
        partner_id: str,
        lines: List[PurchaseInvoiceLine],
        invoice_date: Optional[date] = None,
        supplier_reference: str = "",
        due_date: Optional[date] = None,
        notes: str = ""
    ) -> PurchaseInvoice:
        """Create a new purchase invoice."""
        if not invoice_date:
            invoice_date = date.today()
        
        if not due_date:
            due_date = invoice_date + timedelta(days=30)
        
        # Generate invoice number
        invoice_number = self._repo.get_next_invoice_number()
        
        invoice = PurchaseInvoice(
            invoice_number=invoice_number,
            partner_id=partner_id,
            invoice_date=invoice_date,
            due_date=due_date,
            supplier_reference=supplier_reference,
            lines=lines,
            status=PurchaseInvoiceStatus.DRAFT,
            notes=notes
        )
        
        return self._repo.save(invoice)
    
    def create_from_order(self, order_id: str) -> PurchaseInvoice:
        """Create invoice from purchase order."""
        order = self._order_repo.find_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        if order.status != PurchaseOrderStatus.RECEIVED:
            raise ValueError("Order must be received first")
        
        # Convert order lines to invoice lines
        invoice_lines = [
            PurchaseInvoiceLine(
                product_id=line.product_id,
                description=line.description,
                quantity=line.quantity,
                unit_price=line.unit_price,
                tax_rate=line.tax_rate,
                line_number=line.line_number
            )
            for line in order.lines
        ]
        
        invoice = self.create_invoice(
            partner_id=order.partner_id,
            lines=invoice_lines,
            invoice_date=date.today(),
            supplier_reference=f"PO-{order.order_number}",
            notes=f"Generated from {order.order_number}"
        )
        
        invoice.purchase_order_id = order.id
        
        # Mark order as invoiced
        order.status = PurchaseOrderStatus.INVOICED
        self._order_repo.save(order)
        
        return self._repo.save(invoice)
    
    def post_invoice(self, invoice_id: str) -> PurchaseInvoice:
        """Post invoice to accounting."""
        invoice = self._repo.find_by_id(invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")
        
        if invoice.status != PurchaseInvoiceStatus.DRAFT:
            raise ValueError("Only draft invoices can be posted")
        
        # Get partner
        partner = self._partner_repo.find_by_id(invoice.partner_id)
        if not partner:
            raise ValueError("Supplier not found")
        
        # Create journal entry
        description = f"Factura Compra {invoice.supplier_reference or invoice.invoice_number} - {partner.name}"
        
        # Determine accounts using mapping service
        expense_account = self._mapping.get_purchase_account()  # 600
        vat_account = self._mapping.get_input_vat_account()     # 472
        payable_account = self._mapping.get_accounts_payable_account()  # 400
        
        entry_lines = [
            {
                "account_code": expense_account.code,
                "debit": float(invoice.subtotal),
                "credit": 0.0,
                "description": description
            },
            {
                "account_code": vat_account.code,
                "debit": float(invoice.tax_amount),
                "credit": 0.0,
                "description": f"IVA Suportat ({int(invoice.lines[0].tax_rate if invoice.lines else 21)}%)"
            },
            {
                "account_code": payable_account.code,
                "debit": 0.0,
                "credit": float(invoice.total_amount),
                "description": f"Proveïdor: {partner.name}"
            }
        ]
        
        journal_entry = self._accounting.create_journal_entry(
            date=invoice.invoice_date,
            description=description,
            lines=entry_lines
        )
        
        invoice.journal_entry_id = journal_entry.id
        invoice.status = PurchaseInvoiceStatus.POSTED
        
        # Update inventory if not from order
        if not invoice.purchase_order_id and self._inventory:
            for line in invoice.lines:
                if line.product_id:
                    try:
                        self._inventory.record_purchase(
                            product_id=line.product_id,
                            quantity=line.quantity,
                            reference=f"PI-{invoice.invoice_number}"
                        )
                    except Exception as e:
                        logger.warning(f"Inventory update failed: {e}")
        
        # Audit
        if self._audit:
            self._audit.log(
                entity_type="PurchaseInvoice",
                entity_id=invoice.id,
                action="POST",
                user_id="system",
                details=f"Posted invoice {invoice.invoice_number}"
            )
        
        return self._repo.save(invoice)
    
    def mark_paid(
        self,
        invoice_id: str,
        payment_date: date,
        amount: Decimal,
        bank_account_code: str = "572"
    ) -> PurchaseInvoice:
        """Mark invoice as paid (full or partial)."""
        invoice = self._repo.find_by_id(invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")
        
        if invoice.status != PurchaseInvoiceStatus.POSTED:
            raise ValueError("Only posted invoices can be marked as paid")
        
        # Get partner
        partner = self._partner_repo.find_by_id(invoice.partner_id)
        
        # Create payment entry
        payable_account = self._mapping.get_accounts_payable_account()
        
        description = f"Pagament {invoice.supplier_reference or invoice.invoice_number}"
        
        entry_lines = [
            {
                "account_code": payable_account.code,
                "debit": float(amount),
                "credit": 0.0,
                "description": f"Pagament a {partner.name if partner else 'Proveïdor'}"
            },
            {
                "account_code": bank_account_code,
                "debit": 0.0,
                "credit": float(amount),
                "description": description
            }
        ]
        
        self._accounting.create_journal_entry(
            date=payment_date,
            description=description,
            lines=entry_lines
        )
        
        # Update invoice
        invoice.amount_paid += amount
        
        if invoice.amount_paid >= invoice.total_amount:
            invoice.payment_status = PaymentStatus.PAID
            invoice.status = PurchaseInvoiceStatus.PAID
        else:
            invoice.payment_status = PaymentStatus.PARTIAL
        
        return self._repo.save(invoice)
    
    def get_invoice(self, invoice_id: str) -> Optional[PurchaseInvoice]:
        """Get purchase invoice by ID."""
        return self._repo.find_by_id(invoice_id)
    
    def list_invoices(
        self,
        status: Optional[PurchaseInvoiceStatus] = None,
        partner_id: Optional[str] = None
    ) -> List[PurchaseInvoice]:
        """List purchase invoices."""
        if status:
            return self._repo.list_by_status(status)
        elif partner_id:
            return self._repo.list_by_partner(partner_id)
        return self._repo.list_all()
