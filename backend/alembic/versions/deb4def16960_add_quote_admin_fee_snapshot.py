"""add quote admin fee snapshot

Revision ID: deb4def16960
Revises: 52b3145281e0
Create Date: 2026-02-03 05:02:46.424324+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'deb4def16960'
down_revision = '52b3145281e0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("quotes")}

    if "admin_fee_percent" not in columns:
        op.add_column("quotes", sa.Column("admin_fee_percent", sa.Float(), nullable=True))
    if "admin_discount_percent" not in columns:
        op.add_column("quotes", sa.Column("admin_discount_percent", sa.Float(), nullable=True))
    if "calculation_breakdown" not in columns:
        op.add_column("quotes", sa.Column("calculation_breakdown", sa.JSON(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("quotes")}

    if "calculation_breakdown" in columns:
        op.drop_column("quotes", "calculation_breakdown")
    if "admin_discount_percent" in columns:
        op.drop_column("quotes", "admin_discount_percent")
    if "admin_fee_percent" in columns:
        op.drop_column("quotes", "admin_fee_percent")
