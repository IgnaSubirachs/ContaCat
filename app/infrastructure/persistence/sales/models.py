from sqlalchemy import Column, String, Integer, Date, Numeric, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import date

from app.infrastructure.db.base import Base
from app.domain.sales.entities import QuoteStatus, OrderStatus, InvoiceStatus, PaymentStatus


class SalesLineModel(Base):
    """SQLAlchemy model for sales lines (shared by quotes, orders, invoices)."""
    __tablename__ = "sales_lines"
    
    id = Column(String(36), primary_key=True)
    product_code = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    tax_rate = Column(Numeric(5, 2), default=21)
    
    # Relationships (polymorphic - can belong to quote, order, or invoice)
    quote_id = Column(String(36), ForeignKey("quotes.id"), nullable=True)
    order_id = Column(String(36), ForeignKey("sales_orders.id"), nullable=True)
    invoice_id = Column(String(36), ForeignKey("sales_invoices.id"), nullable=True)


class QuoteModel(Base):
    """SQLAlchemy model for quotes (pressupostos)."""
    __tablename__ = "quotes"
    
    id = Column(String(36), primary_key=True)
    quote_number = Column(String(50), unique=True, nullable=False, index=True)
    quote_date = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=False)
    partner_id = Column(String(36), nullable=False, index=True)
    status = Column(SQLEnum(QuoteStatus), default=QuoteStatus.DRAFT, nullable=False)
    notes = Column(Text, default="")
    
    # Relationships
    lines = relationship("SalesLineModel", foreign_keys=[SalesLineModel.quote_id], cascade="all, delete-orphan")


class SalesOrderModel(Base):
    """SQLAlchemy model for sales orders (comandes)."""
    __tablename__ = "sales_orders"
    
    id = Column(String(36), primary_key=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    order_date = Column(Date, nullable=False)
    partner_id = Column(String(36), nullable=False, index=True)
    quote_id = Column(String(36), nullable=True)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.DRAFT, nullable=False)
    delivery_date = Column(Date, nullable=True)
    delivery_address = Column(Text, default="")
    notes = Column(Text, default="")
    
    # Relationships
    lines = relationship("SalesLineModel", foreign_keys=[SalesLineModel.order_id], cascade="all, delete-orphan")


class SalesInvoiceModel(Base):
    """SQLAlchemy model for sales invoices (factures)."""
    __tablename__ = "sales_invoices"
    
    id = Column(String(36), primary_key=True)
    series = Column(String(10), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    number = Column(Integer, nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    partner_id = Column(String(36), nullable=False, index=True)
    order_id = Column(String(36), nullable=True)
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    journal_entry_id = Column(String(36), nullable=True)
    notes = Column(Text, default="")
    
    # Relationships
    lines = relationship("SalesLineModel", foreign_keys=[SalesLineModel.invoice_id], cascade="all, delete-orphan")
