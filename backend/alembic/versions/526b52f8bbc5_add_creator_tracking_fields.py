"""add_creator_tracking_fields

Revision ID: 526b52f8bbc5
Revises: 77b4523e2a56
Create Date: 2025-12-21 04:46:08.642341+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '526b52f8bbc5'
down_revision = '77b4523e2a56'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # policies: add sales_agent_id
    op.add_column('policies', sa.Column('sales_agent_id', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'policies', 'users', ['sales_agent_id'], ['id'])

    # claims: add created_by
    op.add_column('claims', sa.Column('created_by', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'claims', 'users', ['created_by'], ['id'])

    # clients: add created_by
    op.add_column('clients', sa.Column('created_by', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'clients', 'users', ['created_by'], ['id'])

    # users: add created_by
    op.add_column('users', sa.Column('created_by', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'users', 'users', ['created_by'], ['id'])


def downgrade() -> None:
    # users
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'created_by')

    # clients
    op.drop_constraint(None, 'clients', type_='foreignkey')
    op.drop_column('clients', 'created_by')

    # claims
    op.drop_constraint(None, 'claims', type_='foreignkey')
    op.drop_column('claims', 'created_by')

    # policies
    op.drop_constraint(None, 'policies', type_='foreignkey')
    op.drop_column('policies', 'sales_agent_id')
