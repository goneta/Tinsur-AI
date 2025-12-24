"""Initial migration - Create companies, users, and clients tables

Revision ID: 001
Revises: 
Create Date: 2025-12-12 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('subdomain', sa.String(100), unique=True, nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(50)),
        sa.Column('address', sa.Text()),
        sa.Column('logo_url', sa.String(500)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('features', JSONB, default={}),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE')),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('phone', sa.String(50)),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('mfa_enabled', sa.Boolean(), default=False),
        sa.Column('mfa_secret', sa.String(255)),
        sa.Column('last_login', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    # Create clients table
    op.create_table(
        'clients',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('client_type', sa.String(50), nullable=False),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('business_name', sa.String(255)),
        sa.Column('email', sa.String(255)),
        sa.Column('phone', sa.String(50)),
        sa.Column('date_of_birth', sa.Date()),
        sa.Column('gender', sa.String(20)),
        sa.Column('address', sa.Text()),
        sa.Column('city', sa.String(100)),
        sa.Column('country', sa.String(100), default='Côte d\'Ivoire'),
        sa.Column('id_number', sa.String(100)),
        sa.Column('driving_licence_number', sa.String(100)),
        sa.Column('tax_id', sa.String(100)),
        sa.Column('risk_profile', sa.String(50), default='medium'),
        sa.Column('status', sa.String(50), default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    # Create indexes
    op.create_index('idx_users_company_id', 'users', ['company_id'])
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_clients_company_id', 'clients', ['company_id'])
    op.create_index('idx_clients_email', 'clients', ['email'])


def downgrade() -> None:
    op.drop_index('idx_clients_email', 'clients')
    op.drop_index('idx_clients_company_id', 'clients')
    op.drop_index('idx_users_email', 'users')
    op.drop_index('idx_users_company_id', 'users')
    op.drop_table('clients')
    op.drop_table('users')
    op.drop_table('companies')
