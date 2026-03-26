"""recreate_referrals_manual

Revision ID: 41024cc3049e
Revises: 03fcdcc14ed8
Create Date: 2026-01-15 19:25:12.878708+00:00

"""
from alembic import op
import sqlalchemy as sa
import uuid
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '41024cc3049e'
down_revision = '03fcdcc14ed8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Safely recreate referrals table to fix any schema mismatch
    op.execute("DROP TABLE IF EXISTS referrals")
    
    op.create_table(
        'referrals',
        sa.Column('id', sa.UUID(), nullable=False, primary_key=True),
        sa.Column('company_id', sa.UUID(), nullable=True),
        sa.Column('referrer_client_id', sa.UUID(), nullable=True),
        sa.Column('referred_client_id', sa.UUID(), nullable=True),
        sa.Column('referral_code', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True, default='pending'),
        sa.Column('reward_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('reward_paid', sa.Boolean(), nullable=True, default=False),
        sa.Column('converted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        
        sa.UniqueConstraint('referral_code'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['referrer_client_id'], ['clients.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['referred_client_id'], ['clients.id'], ondelete='SET NULL'),
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS referrals")
