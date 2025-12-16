"""SQLAlchemy models for purchase module."""
from sqlalchemy import Column, String, Date, Integer, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base


class PurchaseOrderModel(Base):
    """Purchase Order model."""
    __tablename__ = "purchase_orders"
    
    id = Column(String(36), primary_key=True)
    order_number = Column(String(50), unique=True, nullable=False)
    order_date = Column(Date, nullable=False)
    partner_id = Column(String(36), ForeignKey("partners.id"), nullable=False)
    status = Column(String(20), nullable=False)
    notes = Column(Text)
    
    # Computed totals
    subtotal = Column(Numeric(15, 2))
    tax_amount = Column(Numeric(15, 2))
    total_amount = Column(Numeric(15, 2))
    
    # Relationships
    lines = relationship("PurchaseOrderLineModel", back_populates="order", cascade="all, delete-orphan")


class PurchaseOrderLineModel(Base):
    """Purchase Order Line model."""
    __tablename__ = "purchase_order_lines"
    
    id = Column(String(36), primary_key=True)
    purchase_order_id = Column(String(36), ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=True)
    description = Column(Text, nullable=False)
    quantity = Column(Numeric(15, 2), nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), default=21.00)
    tax_amount = Column(Numeric(15, 2))
    total = Column(Numeric(15, 2))
    line_number = Column(Integer, default=1)
    
    # Relationships
    order = relationship("PurchaseOrderModel", back_populates="lines")


class PurchaseInvoiceModel(Base):
    """Purchase Invoice model."""
    __tablename__ = "purchase_invoices"
    
    id = Column(String(36), primary_key=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    supplier_reference = Column(String(100))  # Supplier's invoice number
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date)
    partner_id = Column(String(36), ForeignKey("partners.id"), nullable=False)
    purchase_order_id = Column(String(36), ForeignKey("purchase_orders.id"), nullable=True)
    status = Column(String(20), nullable=False)
    payment_status = Column(String(20))
    notes = Column(Text)
    
    # Financial
    subtotal = Column(Numeric(15, 2))
    tax_amount = Column(Numeric(15, 2))
    total_amount = Column(Numeric(15, 2))
    amount_paid = Column(Numeric(15, 2), default=0.00)
    
    # Accounting link
    journal_entry_id = Column(String(36))
    
    # Relationships
    lines = relationship("PurchaseInvoiceLineModel", back_populates="invoice", cascade="all, delete-orphan")


class PurchaseInvoiceLineModel(Base):
    """Purchase Invoice Line model."""
    __tablename__ = "purchase_invoice_lines"
    
    id = Column(String(36), primary_key=True)
    purchase_invoice_id = Column(String(36), ForeignKey("purchase_invoices.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=True)
    description = Column(Text, nullable=False)
    quantity = Column(Numeric(15, 2), nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), default=21.00)
    tax_amount = Column(Numeric(15, 2))
    total = Column(Numeric(15, 2))
    line_number = Column(Integer, default=1)
    
    # Relationships
    invoice = relationship("PurchaseInvoiceModel", back_populates="lines")
