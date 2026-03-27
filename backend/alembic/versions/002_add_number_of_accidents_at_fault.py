"""Add number_of_accidents_at_fault field to clients and drivers tables

Revision ID: 002
Revises: 001
Create Date: 2026-03-27 22:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add number_of_accidents_at_fault column to clients and client_drivers tables."""
    # Add column to clients table
    op.add_column('clients', 
                  sa.Column('number_of_accidents_at_fault', sa.Integer(), 
                           nullable=False, server_default='0'))
    
    # Add column to client_drivers table
    op.add_column('client_drivers',
                  sa.Column('number_of_accidents_at_fault', sa.Integer(),
                           nullable=False, server_default='0'))


def downgrade() -> None:
    """Remove number_of_accidents_at_fault column from clients and client_drivers tables."""
    # Remove column from client_drivers table
    op.drop_column('client_drivers', 'number_of_accidents_at_fault')
    
    # Remove column from clients table
    op.drop_column('clients', 'number_of_accidents_at_fault')
