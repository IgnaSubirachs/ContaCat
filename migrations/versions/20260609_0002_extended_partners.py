"""extended partner profile

Revision ID: 20260609_0002
Revises: 20260604_0001
Create Date: 2026-06-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260609_0002"
down_revision: Union[str, None] = "20260604_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


FIELDS = (
    ("trade_name", sa.String(200), ""),
    ("contact_person", sa.String(150), ""),
    ("mobile", sa.String(20), ""),
    ("website", sa.String(255), ""),
    ("customer_code", sa.String(50), ""),
    ("supplier_code", sa.String(50), ""),
    ("relationship_status", sa.String(20), "ACTIVE"),
    ("relationship_since", sa.Date(), None),
    ("sales_representative", sa.String(150), ""),
    ("price_list", sa.String(100), ""),
    ("default_discount", sa.Float(), "0"),
    ("credit_limit", sa.Float(), "0"),
    ("payment_day", sa.Integer(), "0"),
    ("customer_account", sa.String(20), ""),
    ("supplier_account", sa.String(20), ""),
    ("bank_name", sa.String(150), ""),
    ("bank_account_holder", sa.String(200), ""),
    ("swift_bic", sa.String(11), ""),
    ("contract_summary", sa.Text(), ""),
    ("accrual_notes", sa.Text(), ""),
    ("internal_notes", sa.Text(), ""),
)


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table("partners"):
        return
    existing = {column["name"] for column in inspector.get_columns("partners")}
    for name, column_type, default in FIELDS:
        if name in existing:
            continue
        kwargs = {"nullable": True}
        if default is not None:
            kwargs["server_default"] = default
        op.add_column("partners", sa.Column(name, column_type, **kwargs))


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table("partners"):
        return
    existing = {column["name"] for column in inspector.get_columns("partners")}
    for name, _, _ in reversed(FIELDS):
        if name in existing:
            op.drop_column("partners", name)
