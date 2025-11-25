from typing import List, Optional
from sqlalchemy.orm import Session
from decimal import Decimal

from app.domain.sales.entities import (
    Quote, SalesOrder, SalesInvoice, SalesLine,
    QuoteStatus, OrderStatus, InvoiceStatus
)
from app.domain.sales.repositories import (
    QuoteRepository, SalesOrderRepository, SalesInvoiceRepository
)
from app.infrastructure.persistence.sales.models import (
    QuoteModel, SalesOrderModel, SalesInvoiceModel, SalesLineModel
)


class SqlAlchemyQuoteRepository(QuoteRepository):
    """SQLAlchemy implementation of QuoteRepository."""
    
    def __init__(self, session: Session):
        self._session = session
    
    def _to_entity(self, model: QuoteModel) -> Quote:
        """Convert model to entity."""
        lines = [
            SalesLine(
                id=line.id,
                product_code=line.product_code,
                description=line.description,
                quantity=Decimal(str(line.quantity)),
                unit_price=Decimal(str(line.unit_price)),
                discount_percent=Decimal(str(line.discount_percent)),
                tax_rate=Decimal(str(line.tax_rate))
            )
            for line in model.lines
        ]
        
        return Quote(
            id=model.id,
            quote_number=model.quote_number,
            quote_date=model.quote_date,
            valid_until=model.valid_until,
            partner_id=model.partner_id,
            lines=lines,
            status=model.status,
            notes=model.notes
        )
    
    def _to_model(self, entity: Quote) -> QuoteModel:
        """Convert entity to model."""
        model = QuoteModel(
            id=entity.id,
            quote_number=entity.quote_number,
            quote_date=entity.quote_date,
            valid_until=entity.valid_until,
            partner_id=entity.partner_id,
            status=entity.status,
            notes=entity.notes
        )
        
        # Add lines
        for line in entity.lines:
            line_model = SalesLineModel(
                id=line.id,
                product_code=line.product_code,
                description=line.description,
                quantity=float(line.quantity),
                unit_price=float(line.unit_price),
                discount_percent=float(line.discount_percent),
                tax_rate=float(line.tax_rate),
                quote_id=entity.id
            )
            model.lines.append(line_model)
        
        return model
    
    def add(self, quote: Quote) -> None:
        model = self._to_model(quote)
        self._session.add(model)
        self._session.commit()
    
    def update(self, quote: Quote) -> None:
        # Delete existing lines
        self._session.query(SalesLineModel).filter(
            SalesLineModel.quote_id == quote.id
        ).delete()
        
        # Update quote
        model = self._session.query(QuoteModel).filter(QuoteModel.id == quote.id).first()
        if model:
            model.quote_number = quote.quote_number
            model.quote_date = quote.quote_date
            model.valid_until = quote.valid_until
            model.partner_id = quote.partner_id
            model.status = quote.status
            model.notes = quote.notes
            
            # Add new lines
            for line in quote.lines:
                line_model = SalesLineModel(
                    id=line.id,
                    product_code=line.product_code,
                    description=line.description,
                    quantity=float(line.quantity),
                    unit_price=float(line.unit_price),
                    discount_percent=float(line.discount_percent),
                    tax_rate=float(line.tax_rate),
                    quote_id=quote.id
                )
                self._session.add(line_model)
            
            self._session.commit()
    
    def delete(self, quote_id: str) -> None:
        self._session.query(QuoteModel).filter(QuoteModel.id == quote_id).delete()
        self._session.commit()
    
    def find_by_id(self, quote_id: str) -> Optional[Quote]:
        model = self._session.query(QuoteModel).filter(QuoteModel.id == quote_id).first()
        return self._to_entity(model) if model else None
    
    def find_by_number(self, quote_number: str) -> Optional[Quote]:
        model = self._session.query(QuoteModel).filter(QuoteModel.quote_number == quote_number).first()
        return self._to_entity(model) if model else None
    
    def list_all(self) -> List[Quote]:
        models = self._session.query(QuoteModel).order_by(QuoteModel.quote_date.desc()).all()
        return [self._to_entity(model) for model in models]
    
    def list_by_partner(self, partner_id: str) -> List[Quote]:
        models = self._session.query(QuoteModel).filter(
            QuoteModel.partner_id == partner_id
        ).order_by(QuoteModel.quote_date.desc()).all()
        return [self._to_entity(model) for model in models]
    
    def list_by_status(self, status: QuoteStatus) -> List[Quote]:
        models = self._session.query(QuoteModel).filter(
            QuoteModel.status == status
        ).order_by(QuoteModel.quote_date.desc()).all()
        return [self._to_entity(model) for model in models]
    
    def get_next_quote_number(self) -> str:
        # Get last quote number
        last_quote = self._session.query(QuoteModel).order_by(
            QuoteModel.quote_number.desc()
        ).first()
        
        if last_quote:
            # Extract number from format "PRE-2025-001"
            try:
                parts = last_quote.quote_number.split("-")
                if len(parts) == 3:
                    last_num = int(parts[2])
                    return f"PRE-{parts[1]}-{last_num + 1:03d}"
            except:
                pass
        
        # Default: PRE-YEAR-001
        from datetime import date
        return f"PRE-{date.today().year}-001"


class SqlAlchemySalesOrderRepository(SalesOrderRepository):
    """SQLAlchemy implementation of SalesOrderRepository."""
    
    def __init__(self, session: Session):
        self._session = session
    
    def _to_entity(self, model: SalesOrderModel) -> SalesOrder:
        """Convert model to entity."""
        lines = [
            SalesLine(
                id=line.id,
                product_code=line.product_code,
                description=line.description,
                quantity=Decimal(str(line.quantity)),
                unit_price=Decimal(str(line.unit_price)),
                discount_percent=Decimal(str(line.discount_percent)),
                tax_rate=Decimal(str(line.tax_rate))
            )
            for line in model.lines
        ]
        
        return SalesOrder(
            id=model.id,
            order_number=model.order_number,
            order_date=model.order_date,
            partner_id=model.partner_id,
            lines=lines,
            status=model.status,
            quote_id=model.quote_id,
            delivery_date=model.delivery_date,
            delivery_address=model.delivery_address,
            notes=model.notes
        )
    
    def _to_model(self, entity: SalesOrder) -> SalesOrderModel:
        """Convert entity to model."""
        model = SalesOrderModel(
            id=entity.id,
            order_number=entity.order_number,
            order_date=entity.order_date,
            partner_id=entity.partner_id,
            quote_id=entity.quote_id,
            status=entity.status,
            delivery_date=entity.delivery_date,
            delivery_address=entity.delivery_address,
            notes=entity.notes
        )
        
        # Add lines
        for line in entity.lines:
            line_model = SalesLineModel(
                id=line.id,
                product_code=line.product_code,
                description=line.description,
                quantity=float(line.quantity),
                unit_price=float(line.unit_price),
                discount_percent=float(line.discount_percent),
                tax_rate=float(line.tax_rate),
                order_id=entity.id
            )
            model.lines.append(line_model)
        
        return model
    
    def add(self, order: SalesOrder) -> None:
        model = self._to_model(order)
        self._session.add(model)
        self._session.commit()
    
    def update(self, order: SalesOrder) -> None:
        # Delete existing lines
        self._session.query(SalesLineModel).filter(
            SalesLineModel.order_id == order.id
        ).delete()
        
        # Update order
        model = self._session.query(SalesOrderModel).filter(SalesOrderModel.id == order.id).first()
        if model:
            model.order_number = order.order_number
            model.order_date = order.order_date
            model.partner_id = order.partner_id
            model.quote_id = order.quote_id
            model.status = order.status
            model.delivery_date = order.delivery_date
            model.delivery_address = order.delivery_address
            model.notes = order.notes
            
            # Add new lines
            for line in order.lines:
                line_model = SalesLineModel(
                    id=line.id,
                    product_code=line.product_code,
                    description=line.description,
                    quantity=float(line.quantity),
                    unit_price=float(line.unit_price),
                    discount_percent=float(line.discount_percent),
                    tax_rate=float(line.tax_rate),
                    order_id=order.id
                )
                self._session.add(line_model)
            
            self._session.commit()
    
    def delete(self, order_id: str) -> None:
        self._session.query(SalesOrderModel).filter(SalesOrderModel.id == order_id).delete()
        self._session.commit()
    
    def find_by_id(self, order_id: str) -> Optional[SalesOrder]:
        model = self._session.query(SalesOrderModel).filter(SalesOrderModel.id == order_id).first()
        return self._to_entity(model) if model else None
    
    def find_by_number(self, order_number: str) -> Optional[SalesOrder]:
        model = self._session.query(SalesOrderModel).filter(SalesOrderModel.order_number == order_number).first()
        return self._to_entity(model) if model else None
    
    def list_all(self) -> List[SalesOrder]:
        models = self._session.query(SalesOrderModel).order_by(SalesOrderModel.order_date.desc()).all()
        return [self._to_entity(model) for model in models]
    
    def list_by_partner(self, partner_id: str) -> List[SalesOrder]:
        models = self._session.query(SalesOrderModel).filter(
            SalesOrderModel.partner_id == partner_id
        ).order_by(SalesOrderModel.order_date.desc()).all()
        return [self._to_entity(model) for model in models]
    
    def list_by_status(self, status: OrderStatus) -> List[SalesOrder]:
        models = self._session.query(SalesOrderModel).filter(
            SalesOrderModel.status == status
        ).order_by(SalesOrderModel.order_date.desc()).all()
        return [self._to_entity(model) for model in models]
    
    def get_next_order_number(self) -> str:
        # Get last order number
        last_order = self._session.query(SalesOrderModel).order_by(
            SalesOrderModel.order_number.desc()
        ).first()
        
        if last_order:
            # Extract number from format "ORD-2025-001"
            try:
                parts = last_order.order_number.split("-")
                if len(parts) == 3:
                    last_num = int(parts[2])
                    return f"ORD-{parts[1]}-{last_num + 1:03d}"
            except:
                pass
        
        # Default: ORD-YEAR-001
        from datetime import date
        return f"ORD-{date.today().year}-001"


class SqlAlchemySalesInvoiceRepository(SalesInvoiceRepository):
    """SQLAlchemy implementation of SalesInvoiceRepository."""
    
    def __init__(self, session: Session):
        self._session = session
    
    def _to_entity(self, model: SalesInvoiceModel) -> SalesInvoice:
        """Convert model to entity."""
        lines = [
            SalesLine(
                id=line.id,
                product_code=line.product_code,
                description=line.description,
                quantity=Decimal(str(line.quantity)),
                unit_price=Decimal(str(line.unit_price)),
                discount_percent=Decimal(str(line.discount_percent)),
                tax_rate=Decimal(str(line.tax_rate))
            )
            for line in model.lines
        ]
        
        return SalesInvoice(
            id=model.id,
            series=model.series,
            year=model.year,
            number=model.number,
            invoice_date=model.invoice_date,
            due_date=model.due_date,
            partner_id=model.partner_id,
            lines=lines,
            status=model.status,
            payment_status=model.payment_status,
            order_id=model.order_id,
            journal_entry_id=model.journal_entry_id,
            notes=model.notes
        )
    
    def _to_model(self, entity: SalesInvoice) -> SalesInvoiceModel:
        """Convert entity to model."""
        model = SalesInvoiceModel(
            id=entity.id,
            series=entity.series,
            year=entity.year,
            number=entity.number,
            invoice_date=entity.invoice_date,
            due_date=entity.due_date,
            partner_id=entity.partner_id,
            order_id=entity.order_id,
            status=entity.status,
            payment_status=entity.payment_status,
            journal_entry_id=entity.journal_entry_id,
            notes=entity.notes
        )
        
        # Add lines
        for line in entity.lines:
            line_model = SalesLineModel(
                id=line.id,
                product_code=line.product_code,
                description=line.description,
                quantity=float(line.quantity),
                unit_price=float(line.unit_price),
                discount_percent=float(line.discount_percent),
                tax_rate=float(line.tax_rate),
                invoice_id=entity.id
            )
            model.lines.append(line_model)
        
        return model
    
    def add(self, invoice: SalesInvoice) -> None:
        model = self._to_model(invoice)
        self._session.add(model)
        self._session.commit()
    
    def update(self, invoice: SalesInvoice) -> None:
        # Delete existing lines
        self._session.query(SalesLineModel).filter(
            SalesLineModel.invoice_id == invoice.id
        ).delete()
        
        # Update invoice
        model = self._session.query(SalesInvoiceModel).filter(SalesInvoiceModel.id == invoice.id).first()
        if model:
            model.series = invoice.series
            model.year = invoice.year
            model.number = invoice.number
            model.invoice_date = invoice.invoice_date
            model.due_date = invoice.due_date
            model.partner_id = invoice.partner_id
            model.order_id = invoice.order_id
            model.status = invoice.status
            model.payment_status = invoice.payment_status
            model.journal_entry_id = invoice.journal_entry_id
            model.notes = invoice.notes
            
            # Add new lines
            for line in invoice.lines:
                line_model = SalesLineModel(
                    id=line.id,
                    product_code=line.product_code,
                    description=line.description,
                    quantity=float(line.quantity),
                    unit_price=float(line.unit_price),
                    discount_percent=float(line.discount_percent),
                    tax_rate=float(line.tax_rate),
                    invoice_id=invoice.id
                )
                self._session.add(line_model)
            
            self._session.commit()
    
    def delete(self, invoice_id: str) -> None:
        self._session.query(SalesInvoiceModel).filter(SalesInvoiceModel.id == invoice_id).delete()
        self._session.commit()
    
    def find_by_id(self, invoice_id: str) -> Optional[SalesInvoice]:
        model = self._session.query(SalesInvoiceModel).filter(SalesInvoiceModel.id == invoice_id).first()
        return self._to_entity(model) if model else None
    
    def find_by_number(self, series: str, year: int, number: int) -> Optional[SalesInvoice]:
        model = self._session.query(SalesInvoiceModel).filter(
            SalesInvoiceModel.series == series,
            SalesInvoiceModel.year == year,
            SalesInvoiceModel.number == number
        ).first()
        return self._to_entity(model) if model else None
    
    def list_all(self) -> List[SalesInvoice]:
        models = self._session.query(SalesInvoiceModel).order_by(
            SalesInvoiceModel.year.desc(),
            SalesInvoiceModel.number.desc()
        ).all()
        return [self._to_entity(model) for model in models]
    
    def list_by_partner(self, partner_id: str) -> List[SalesInvoice]:
        models = self._session.query(SalesInvoiceModel).filter(
            SalesInvoiceModel.partner_id == partner_id
        ).order_by(
            SalesInvoiceModel.year.desc(),
            SalesInvoiceModel.number.desc()
        ).all()
        return [self._to_entity(model) for model in models]
    
    def list_by_status(self, status: InvoiceStatus) -> List[SalesInvoice]:
        models = self._session.query(SalesInvoiceModel).filter(
            SalesInvoiceModel.status == status
        ).order_by(
            SalesInvoiceModel.year.desc(),
            SalesInvoiceModel.number.desc()
        ).all()
        return [self._to_entity(model) for model in models]
    
    def get_next_invoice_number(self, series: str, year: int) -> int:
        # Get last invoice number for this series and year
        last_invoice = self._session.query(SalesInvoiceModel).filter(
            SalesInvoiceModel.series == series,
            SalesInvoiceModel.year == year
        ).order_by(SalesInvoiceModel.number.desc()).first()
        
        if last_invoice:
            return last_invoice.number + 1
        else:
            return 1
