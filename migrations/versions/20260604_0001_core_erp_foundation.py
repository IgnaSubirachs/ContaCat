"""core erp foundation

Revision ID: 20260604_0001
Revises: None
Create Date: 2026-06-04
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260604_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=False),
        sa.Column("tax_id", sa.String(length=50), nullable=False),
        sa.Column("country", sa.String(length=2), nullable=False, server_default="ES"),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="EUR"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_companies_tax_id", "companies", ["tax_id"], unique=True)

    op.create_table(
        "warehouses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id", "code", name="uq_warehouses_company_code"),
    )
    op.create_index("ix_warehouses_company_id", "warehouses", ["company_id"])

    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("sku", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("product_type", sa.String(length=20), nullable=False, server_default="GOOD"),
        sa.Column("default_tax_code", sa.String(length=20), nullable=True),
        sa.Column("sales_account_code", sa.String(length=20), nullable=True),
        sa.Column("purchase_account_code", sa.String(length=20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id", "sku", name="uq_products_company_sku"),
    )
    op.create_index("ix_products_company_id", "products", ["company_id"])

    op.create_table(
        "tax_rates",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("tax_type", sa.String(length=20), nullable=False, server_default="VAT"),
        sa.Column("input_account_code", sa.String(length=20), nullable=True),
        sa.Column("output_account_code", sa.String(length=20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id", "code", name="uq_tax_rates_company_code"),
    )
    op.create_index("ix_tax_rates_company_id", "tax_rates", ["company_id"])

    op.create_table(
        "document_sequences",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("document_type", sa.String(length=50), nullable=False),
        sa.Column("series", sa.String(length=20), nullable=False, server_default="A"),
        sa.Column("fiscal_year", sa.Integer(), nullable=False),
        sa.Column("prefix", sa.String(length=30), nullable=False, server_default=""),
        sa.Column("next_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("padding", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id", "document_type", "series", "fiscal_year", name="uq_doc_seq_scope"),
    )
    op.create_index("ix_document_sequences_company_id", "document_sequences", ["company_id"])


def downgrade() -> None:
    op.drop_index("ix_document_sequences_company_id", table_name="document_sequences")
    op.drop_table("document_sequences")
    op.drop_index("ix_tax_rates_company_id", table_name="tax_rates")
    op.drop_table("tax_rates")
    op.drop_index("ix_products_company_id", table_name="products")
    op.drop_table("products")
    op.drop_index("ix_warehouses_company_id", table_name="warehouses")
    op.drop_table("warehouses")
    op.drop_index("ix_companies_tax_id", table_name="companies")
    op.drop_table("companies")
