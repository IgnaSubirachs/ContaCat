"""SQLAlchemy implementations for purchase repositories."""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload

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
from app.infrastructure.persistence.purchases.models import (
    PurchaseOrderModel,
    PurchaseOrderLineModel,
    PurchaseInvoiceModel,
    PurchaseInvoiceLineModel
)


class SqlAlchemyPurchaseOrderRepository(PurchaseOrderRepository):
    """SQLAlchemy implementation of PurchaseOrderRepository."""
    
    def __init__(self, session_factory):
        self._session_factory = session_factory
    
    def save(self, order: PurchaseOrder) -> PurchaseOrder:
        """Save or update purchase order."""
        with self._session_factory() as session:
            # Check if exists
            existing = session.query(PurchaseOrderModel).filter_by(id=order.id).first()
            
            if existing:
                # Update
                existing.order_number = order.order_number
                existing.order_date = order.order_date
                existing.partner_id = order.partner_id
                existing.status = order.status.value
                existing.notes = order.notes
                existing.subtotal = order.subtotal
                existing.tax_amount = order.tax_amount
                existing.total_amount = order.total_amount
                
                # Delete old lines
                session.query(PurchaseOrderLineModel).filter_by(purchase_order_id=order.id).delete()
            else:
                # Create new
                existing = PurchaseOrderModel(
                    id=order.id,
                    order_number=order.order_number,
                    order_date=order.order_date,
                    partner_id=order.partner_id,
                    status=order.status.value,
                    notes=order.notes,
                    subtotal=order.subtotal,
                    tax_amount=order.tax_amount,
                    total_amount=order.total_amount
                )
                session.add(existing)
            
            # Add lines
            for line in order.lines:
                line_model = PurchaseOrderLineModel(
                    id=line.id,
                    purchase_order_id=order.id,
                    product_id=line.product_id,
                    description=line.description,
                    quantity=line.quantity,
                    unit_price=line.unit_price,
                    tax_rate=line.tax_rate,
                    tax_amount=line.tax_amount,
                    total=line.total,
                    line_number=line.line_number
                )
                session.add(line_model)
            
            session.commit()
            return order
    
    def find_by_id(self, order_id: str) -> Optional[PurchaseOrder]:
        """Find order by ID."""
        with self._session_factory() as session:
            model = session.query(PurchaseOrderModel).options(
                joinedload(PurchaseOrderModel.lines)
            ).filter_by(id=order_id).first()
            
            if not model:
                return None
            
            return self._to_entity(model)
    
    def list_all(self) -> List[PurchaseOrder]:
        """List all orders."""
        with self._session_factory() as session:
            models = session.query(PurchaseOrderModel).options(
                joinedload(PurchaseOrderModel.lines)
            ).all()
            return [self._to_entity(m) for m in models]
    
    def list_by_status(self, status: PurchaseOrderStatus) -> List[PurchaseOrder]:
        """List by status."""
        with self._session_factory() as session:
            models = session.query(PurchaseOrderModel).options(
                joinedload(PurchaseOrderModel.lines)
            ).filter_by(status=status.value).all()
            return [self._to_entity(m) for m in models]
    
    def list_by_partner(self, partner_id: str) -> List[PurchaseOrder]:
        """List by supplier."""
        with self._session_factory() as session:
            models = session.query(PurchaseOrderModel).options(
                joinedload(PurchaseOrderModel.lines)
            ).filter_by(partner_id=partner_id).all()
            return [self._to_entity(m) for m in models]
    
    def delete(self, order_id: str) -> bool:
        """Delete order."""
        with self._session_factory() as session:
            result = session.query(PurchaseOrderModel).filter_by(id=order_id).delete()
            session.commit()
            return result > 0
    
    def get_next_order_number(self) -> str:
        """Generate next order number."""
        with self._session_factory() as session:
            last = session.query(PurchaseOrderModel).order_by(
                PurchaseOrderModel.order_number.desc()
            ).first()
            
            if not last:
                return "PO-2025-001"
            
            # Extract number from PO-2025-XXX
            try:
                parts = last.order_number.split("-")
                num = int(parts[-1]) + 1
                return f"PO-2025-{num:03d}"
            except:
                return f"PO-2025-{datetime.now().strftime('%m%d%H%M')}"
    
    def _to_entity(self, model: PurchaseOrderModel) -> PurchaseOrder:
        """Convert model to entity."""
        lines = [
            PurchaseOrderLine(
                id=line.id,
                product_id=line.product_id,
                description=line.description,
                quantity=line.quantity,
                unit_price=line.unit_price,
                tax_rate=line.tax_rate,
                line_number=line.line_number
            )
            for line in sorted(model.lines, key=lambda x: x.line_number)
        ]
        
        return PurchaseOrder(
            id=model.id,
            order_number=model.order_number,
            order_date=model.order_date,
            partner_id=model.partner_id,
            status=PurchaseOrderStatus(model.status),
            lines=lines,
            notes=model.notes or ""
        )


class SqlAlchemyPurchaseInvoiceRepository(PurchaseInvoiceRepository):
    """SQLAlchemy implementation of PurchaseInvoiceRepository."""
    
    def __init__(self, session_factory):
        self._session_factory = session_factory
    
    def save(self, invoice: PurchaseInvoice) -> PurchaseInvoice:
        """Save or update invoice."""
        with self._session_factory() as session:
            existing = session.query(PurchaseInvoiceModel).filter_by(id=invoice.id).first()
            
            if existing:
                existing.invoice_number = invoice.invoice_number
                existing.supplier_reference = invoice.supplier_reference
                existing.invoice_date = invoice.invoice_date
                existing.due_date = invoice.due_date
                existing.partner_id = invoice.partner_id
                existing.purchase_order_id = invoice.purchase_order_id
                existing.status = invoice.status.value
                existing.payment_status = invoice.payment_status.value
                existing.notes = invoice.notes
                existing.subtotal = invoice.subtotal
                existing.tax_amount = invoice.tax_amount
                existing.total_amount = invoice.total_amount
                existing.amount_paid = invoice.amount_paid
                existing.journal_entry_id = invoice.journal_entry_id
                
                session.query(PurchaseInvoiceLineModel).filter_by(purchase_invoice_id=invoice.id).delete()
            else:
                existing = PurchaseInvoiceModel(
                    id=invoice.id,
                    invoice_number=invoice.invoice_number,
                    supplier_reference=invoice.supplier_reference,
                    invoice_date=invoice.invoice_date,
                    due_date=invoice.due_date,
                    partner_id=invoice.partner_id,
                    purchase_order_id=invoice.purchase_order_id,
                    status=invoice.status.value,
                    payment_status=invoice.payment_status.value,
                    notes=invoice.notes,
                    subtotal=invoice.subtotal,
                    tax_amount=invoice.tax_amount,
                    total_amount=invoice.total_amount,
                    amount_paid=invoice.amount_paid,
                    journal_entry_id=invoice.journal_entry_id
                )
                session.add(existing)
            
            for line in invoice.lines:
                line_model = PurchaseInvoiceLineModel(
                    id=line.id,
                    purchase_invoice_id=invoice.id,
                    product_id=line.product_id,
                    description=line.description,
                    quantity=line.quantity,
                    unit_price=line.unit_price,
                    tax_rate=line.tax_rate,
                    tax_amount=line.tax_amount,
                    total=line.total,
                    line_number=line.line_number
                )
                session.add(line_model)
            
            session.commit()
            return invoice
    
    def find_by_id(self, invoice_id: str) -> Optional[PurchaseInvoice]:
        """Find invoice by ID."""
        with self._session_factory() as session:
            model = session.query(PurchaseInvoiceModel).options(
                joinedload(PurchaseInvoiceModel.lines)
            ).filter_by(id=invoice_id).first()
            
            if not model:
                return None
            
            return self._to_entity(model)
    
    def list_all(self) -> List[PurchaseInvoice]:
        """List all invoices."""
        with self._session_factory() as session:
            models = session.query(PurchaseInvoiceModel).options(
                joinedload(PurchaseInvoiceModel.lines)
            ).all()
            return [self._to_entity(m) for m in models]
    
    def list_by_status(self, status: PurchaseInvoiceStatus) -> List[PurchaseInvoice]:
        """List by status."""
        with self._session_factory() as session:
            models = session.query(PurchaseInvoiceModel).options(
                joinedload(PurchaseInvoiceModel.lines)
            ).filter_by(status=status.value).all()
            return [self._to_entity(m) for m in models]
    
    def list_by_partner(self, partner_id: str) -> List[PurchaseInvoice]:
        """List by supplier."""
        with self._session_factory() as session:
            models = session.query(PurchaseInvoiceModel).options(
                joinedload(PurchaseInvoiceModel.lines)
            ).filter_by(partner_id=partner_id).all()
            return [self._to_entity(m) for m in models]
    
    def delete(self, invoice_id: str) -> bool:
        """Delete invoice."""
        with self._session_factory() as session:
            result = session.query(PurchaseInvoiceModel).filter_by(id=invoice_id).delete()
            session.commit()
            return result > 0
    
    def get_next_invoice_number(self) -> str:
        """Generate next invoice number."""
        with self._session_factory() as session:
            last = session.query(PurchaseInvoiceModel).order_by(
                PurchaseInvoiceModel.invoice_number.desc()
            ).first()
            
            if not last:
                return "PI-2025-001"
            
            try:
                parts = last.invoice_number.split("-")
                num = int(parts[-1]) + 1
                return f"PI-2025-{num:03d}"
            except:
                return f"PI-2025-{datetime.now().strftime('%m%d%H%M')}"
    
    def _to_entity(self, model: PurchaseInvoiceModel) -> PurchaseInvoice:
        """Convert model to entity."""
        lines = [
            PurchaseInvoiceLine(
                id=line.id,
                product_id=line.product_id,
                description=line.description,
                quantity=line.quantity,
                unit_price=line.unit_price,
                tax_rate=line.tax_rate,
                line_number=line.line_number
            )
            for line in sorted(model.lines, key=lambda x: x.line_number)
        ]
        
        return PurchaseInvoice(
            id=model.id,
            invoice_number=model.invoice_number,
            supplier_reference=model.supplier_reference or "",
            invoice_date=model.invoice_date,
            due_date=model.due_date,
            partner_id=model.partner_id,
            purchase_order_id=model.purchase_order_id,
            status=PurchaseInvoiceStatus(model.status),
            payment_status=PaymentStatus(model.payment_status),
            amount_paid=model.amount_paid or 0,
            journal_entry_id=model.journal_entry_id,
            lines=lines,
            notes=model.notes or ""
        )
