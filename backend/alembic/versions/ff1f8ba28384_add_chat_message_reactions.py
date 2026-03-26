"""add chat message reactions

Revision ID: ff1f8ba28384
Revises: 037379817dbf
Create Date: 2026-02-03 05:33:33.873256+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'ff1f8ba28384'
down_revision = '037379817dbf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("chat_messages")}
    if "reactions" not in columns:
        op.add_column("chat_messages", sa.Column("reactions", sa.JSON(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("chat_messages")}
    if "reactions" in columns:
        op.drop_column("chat_messages", "reactions")
