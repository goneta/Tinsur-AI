"""add company system_registration_number

Revision ID: 52b3145281e0
Revises: 05a65abc8d6d
Create Date: 2026-02-03 04:55:24.100310+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '52b3145281e0'
down_revision = '05a65abc8d6d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("companies")}
    if "system_registration_number" not in columns:
        op.add_column(
            "companies",
            sa.Column("system_registration_number", sa.String(length=100), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("companies", "system_registration_number")
