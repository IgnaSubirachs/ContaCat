from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.infrastructure.db.base import Base


class CompanyModel(Base):
    """Legal company/tenant for multi-company ERP data separation."""
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    tax_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    country: Mapped[str] = mapped_column(String(2), nullable=False, default="ES")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())


class WarehouseModel(Base):
    """Physical or virtual warehouse owned by a company."""
    __tablename__ = "warehouses"
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_warehouses_company_code"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    company = relationship("CompanyModel")


class ProductModel(Base):
    """Canonical product/service catalog shared by sales, purchases, and inventory."""
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("company_id", "sku", name="uq_products_company_sku"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    product_type: Mapped[str] = mapped_column(String(20), nullable=False, default="GOOD")
    default_tax_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sales_account_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    purchase_account_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    company = relationship("CompanyModel")


class TaxRateModel(Base):
    """Tax definition used by fiscal reports and document lines."""
    __tablename__ = "tax_rates"
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_tax_rates_company_code"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    tax_type: Mapped[str] = mapped_column(String(20), nullable=False, default="VAT")
    input_account_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    output_account_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    company = relationship("CompanyModel")


class DocumentSequenceModel(Base):
    """Transactional numbering source for invoices, orders, and accounting entries."""
    __tablename__ = "document_sequences"
    __table_args__ = (
        UniqueConstraint("company_id", "document_type", "series", "fiscal_year", name="uq_doc_seq_scope"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    series: Mapped[str] = mapped_column(String(20), nullable=False, default="A")
    fiscal_year: Mapped[int] = mapped_column(nullable=False)
    prefix: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    next_number: Mapped[int] = mapped_column(nullable=False, default=1)
    padding: Mapped[int] = mapped_column(nullable=False, default=5)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    company = relationship("CompanyModel")
