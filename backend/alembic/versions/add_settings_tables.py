"""Add settings and company settings fields

Revision ID: add_settings_tables
Revises: 
Create Date: 2025-12-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

# revision identifiers, used by Alembic.
revision = 'add_settings_tables'
down_revision = '002'  # Reference the last migration
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to companies table
    op.add_column('companies', sa.Column('registration_number', sa.String(100), nullable=True))
    op.add_column('companies', sa.Column('bank_details', JSONB, default=[], nullable=True))
    op.add_column('companies', sa.Column('mobile_money_accounts', JSONB, default=[], nullable=True))
    op.add_column('companies', sa.Column('currency', sa.String(10), default='USD', nullable=True))
    op.add_column('companies', sa.Column('country', sa.String(100), nullable=True))
    op.add_column('companies', sa.Column('timezone', sa.String(50), default='UTC', nullable=True))
    
    # Create settings table - MOVED TO NEXT MIGRATION DUE TO FK ISSUE
    # op.create_table(
    #     'settings',
    #     sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    #     sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
    #     sa.Column('theme', sa.String(20), default='light', nullable=True),
    #     sa.Column('language', sa.String(10), default='en', nullable=True),
    #     sa.Column('timezone', sa.String(50), default='UTC', nullable=True),
    #     sa.Column('date_format', sa.String(50), default='MM/DD/YYYY', nullable=True),
    #     sa.Column('currency_format', sa.String(10), default='USD', nullable=True),
    #     sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=True),
    #     sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
    # )
    
    # Set default values for existing companies
    op.execute("""
        UPDATE companies 
        SET bank_details = '[]'::jsonb, 
            mobile_money_accounts = '[]'::jsonb,
            currency = 'USD',
            timezone = 'UTC'
        WHERE bank_details IS NULL
    """)


def downgrade():
    # Drop settings table
    op.drop_table('settings')
    
    # Remove columns from companies table
    op.drop_column('companies', 'timezone')
    op.drop_column('companies', 'country')
    op.drop_column('companies', 'currency')
    op.drop_column('companies', 'mobile_money_accounts')
    op.drop_column('companies', 'bank_details')
    op.drop_column('companies', 'registration_number')
