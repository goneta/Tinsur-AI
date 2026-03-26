"""add sales transactions and targets

Revision ID: 037379817dbf
Revises: deb4def16960
Create Date: 2026-02-03 05:12:31.814082+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from app.core.guid import GUID


# revision identifiers, used by Alembic.
revision = '037379817dbf'
down_revision = 'deb4def16960'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    if "sales_transactions" not in tables:
        op.create_table(
            "sales_transactions",
            sa.Column("id", GUID(), primary_key=True, nullable=False),
            sa.Column("company_id", GUID(), nullable=False),
            sa.Column("policy_id", GUID(), nullable=False),
            sa.Column("employee_id", GUID(), nullable=True),
            sa.Column("pos_location_id", GUID(), nullable=True),
            sa.Column("channel", sa.String(length=50), nullable=False),
            sa.Column("sale_amount", sa.Numeric(15, 2), nullable=False),
            sa.Column("commission_amount", sa.Numeric(15, 2), nullable=True),
            sa.Column("sale_date", sa.Date(), nullable=False),
            sa.Column("sale_time", sa.Time(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["policy_id"], ["policies.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["employee_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["pos_location_id"], ["pos_locations.id"]),
        )

    if "sales_targets" not in tables:
        op.create_table(
            "sales_targets",
            sa.Column("id", GUID(), primary_key=True, nullable=False),
            sa.Column("employee_id", GUID(), nullable=False),
            sa.Column("period", sa.String(length=50), nullable=False),
            sa.Column("target_amount", sa.Numeric(15, 2), nullable=True),
            sa.Column("target_count", sa.Integer(), nullable=True),
            sa.Column("start_date", sa.Date(), nullable=True),
            sa.Column("end_date", sa.Date(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["employee_id"], ["users.id"], ondelete="CASCADE"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    if "sales_transactions" in tables:
        op.drop_table("sales_transactions")
    if "sales_targets" in tables:
        op.drop_table("sales_targets")
