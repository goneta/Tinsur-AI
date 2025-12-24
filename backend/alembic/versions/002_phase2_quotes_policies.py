"""Phase 2 migration - Add policy types, quotes, and policies

Revision ID: 002
Revises: 001
Create Date: 2025-12-12 22:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create policy_types table
    op.create_table(
        'policy_types',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    # Create quotes table
    op.create_table(
        'quotes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE')),
        sa.Column('client_id', UUID(as_uuid=True), sa.ForeignKey('clients.id', ondelete='CASCADE')),
        sa.Column('policy_type_id', UUID(as_uuid=True), sa.ForeignKey('policy_types.id')),
        sa.Column('quote_number', sa.String(50), unique=True, nullable=False),
        sa.Column('coverage_amount', sa.Numeric(15, 2)),
        sa.Column('premium_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('discount_percent', sa.Numeric(5, 2), default=0),
        sa.Column('final_premium', sa.Numeric(15, 2), nullable=False),
        sa.Column('premium_frequency', sa.String(50), default='annual'),
        sa.Column('duration_months', sa.Integer(), default=12),
        sa.Column('risk_score', sa.Numeric(5, 2)),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('valid_until', sa.Date()),
        sa.Column('details', JSONB, default={}),
        sa.Column('notes', sa.Text()),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    # Create policies table
    op.create_table(
        'policies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE')),
        sa.Column('client_id', UUID(as_uuid=True), sa.ForeignKey('clients.id', ondelete='CASCADE')),
        sa.Column('policy_type_id', UUID(as_uuid=True), sa.ForeignKey('policy_types.id')),
        sa.Column('quote_id', UUID(as_uuid=True), sa.ForeignKey('quotes.id'), nullable=True),
        sa.Column('policy_number', sa.String(50), unique=True, nullable=False),
        sa.Column('coverage_amount', sa.Numeric(15, 2)),
        sa.Column('premium_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('premium_frequency', sa.String(50), default='annual'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(50), default='active'),
        sa.Column('cancellation_reason', sa.Text()),
        sa.Column('policy_document_url', sa.String(500)),
        sa.Column('qr_code_data', sa.Text()),
        sa.Column('details', JSONB, default={}),
        sa.Column('notes', sa.Text()),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    # Create indexes
    op.create_index('idx_policy_types_company_id', 'policy_types', ['company_id'])
    op.create_index('idx_quotes_company_id', 'quotes', ['company_id'])
    op.create_index('idx_quotes_client_id', 'quotes', ['client_id'])
    op.create_index('idx_quotes_status', 'quotes', ['status'])
    op.create_index('idx_policies_company_id', 'policies', ['company_id'])
    op.create_index('idx_policies_client_id', 'policies', ['client_id'])
    op.create_index('idx_policies_status', 'policies', ['status'])


def downgrade() -> None:
    op.drop_index('idx_policies_status', 'policies')
    op.drop_index('idx_policies_client_id', 'policies')
    op.drop_index('idx_policies_company_id', 'policies')
    op.drop_index('idx_quotes_status', 'quotes')
    op.drop_index('idx_quotes_client_id', 'quotes')
    op.drop_index('idx_quotes_company_id', 'quotes')
    op.drop_index('idx_policy_types_company_id', 'policy_types')
    op.drop_table('policies')
    op.drop_table('quotes')
    op.drop_table('policy_types')
