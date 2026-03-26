"""add chat channel members

Revision ID: a3c1b9d4c5e7
Revises: ff1f8ba28384
Create Date: 2026-02-03 06:10:00.000000
"""

from alembic import op
import sqlalchemy as sa
from app.core.guid import GUID


# revision identifiers, used by Alembic.
revision = "a3c1b9d4c5e7"
down_revision = "ff1f8ba28384"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "chat_channel_members",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("channel_id", GUID(), nullable=False),
        sa.Column("user_id", GUID(), nullable=False),
        sa.Column("added_by", GUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["channel_id"], ["chat_channels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["added_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_chat_channel_member",
        "chat_channel_members",
        ["channel_id", "user_id"],
        unique=True,
    )


def downgrade():
    op.drop_index("uq_chat_channel_member", table_name="chat_channel_members")
    op.drop_table("chat_channel_members")
