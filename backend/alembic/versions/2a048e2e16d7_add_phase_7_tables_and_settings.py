"""Add Phase 7 tables and Settings (Corrected)

Revision ID: 2a048e2e16d7
Revises: add_settings_tables
Create Date: 2025-12-14 06:04:58.370619+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '2a048e2e16d7'
down_revision = 'add_settings_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create Documents table first (dependency for inter_company_shares)
    op.create_table('documents',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('file_url', sa.String(length=500), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('label', sa.String(length=50), nullable=True),
        sa.Column('visibility', sa.String(length=20), server_default='PRIVATE', nullable=True),
        sa.Column('scope', sa.String(length=20), server_default='B2B', nullable=True),
        sa.Column('is_shareable', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('reshare_rule', sa.String(length=1), server_default='C', nullable=True),
        sa.Column('uploaded_by', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Create Inter-Company Shares
    op.create_table('inter_company_shares',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('from_company_id', sa.UUID(), nullable=False),
        sa.Column('to_company_id', sa.UUID(), nullable=True),
        sa.Column('to_client_id', sa.UUID(), nullable=True),
        sa.Column('to_user_id', sa.UUID(), nullable=True),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.UUID(), nullable=False),
        sa.Column('document_id', sa.UUID(), nullable=True),
        sa.Column('scope', sa.String(length=10), server_default='B2B', nullable=True),
        sa.Column('is_reshareable', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('reshare_rule', sa.String(length=1), nullable=True),
        sa.Column('access_level', sa.String(length=50), server_default='read', nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_revoked', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['from_company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['to_client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['to_company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['to_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Create Claims (Restored)
    op.create_table('claims',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('claim_number', sa.String(length=50), nullable=False),
        sa.Column('policy_id', sa.UUID(), nullable=False),
        sa.Column('client_id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('adjuster_id', sa.UUID(), nullable=True),
        sa.Column('incident_date', sa.Date(), nullable=False),
        sa.Column('incident_description', sa.Text(), nullable=False),
        sa.Column('incident_location', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='submitted', nullable=True),
        sa.Column('claim_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('approved_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('evidence_files', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['adjuster_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['policy_id'], ['policies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('claim_number')
    )

    # 4. Create Tickets
    op.create_table('tickets',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=True),
        sa.Column('client_id', sa.UUID(), nullable=True),
        sa.Column('ticket_number', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('priority', sa.String(length=50), server_default='medium', nullable=True),
        sa.Column('status', sa.String(length=50), server_default='open', nullable=True),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('assigned_to', sa.UUID(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('sla_breach_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticket_number')
    )

    # 5. Other specialized tables
    op.create_table('referrals',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=True),
        sa.Column('referrer_client_id', sa.UUID(), nullable=True),
        sa.Column('referred_client_id', sa.UUID(), nullable=True),
        sa.Column('referral_code', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='pending', nullable=True),
        sa.Column('reward_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('reward_paid', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('converted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['referred_client_id'], ['clients.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['referrer_client_id'], ['clients.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('referral_code')
    )

    op.create_table('loyalty_points',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('client_id', sa.UUID(), nullable=True),
        sa.Column('points_earned', sa.Integer(), server_default='0', nullable=True),
        sa.Column('points_redeemed', sa.Integer(), server_default='0', nullable=True),
        sa.Column('points_balance', sa.Integer(), server_default='0', nullable=True),
        sa.Column('tier', sa.String(length=50), server_default='bronze', nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('telematics_data',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('policy_id', sa.UUID(), nullable=True),
        sa.Column('device_id', sa.String(length=255), nullable=False),
        sa.Column('trip_date', sa.Date(), nullable=False),
        sa.Column('distance_km', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('avg_speed', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('max_speed', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('harsh_braking_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('harsh_acceleration_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('night_driving_km', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('safety_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['policy_id'], ['policies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('ml_models',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('model_name', sa.String(length=255), nullable=False),
        sa.Column('model_type', sa.String(length=100), nullable=True),
        sa.Column('model_version', sa.String(length=50), nullable=True),
        sa.Column('accuracy', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('deployed_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('share_codes',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('creator_id', sa.UUID(), nullable=False),
        sa.Column('share_type', sa.String(length=10), nullable=False),
        sa.Column('recipient_ids', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='active', nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_share_codes_code'), 'share_codes', ['code'], unique=True)

    # 6. Client Detail Tables
    op.create_table('client_automobile',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('client_id', sa.UUID(), nullable=True),
        sa.Column('vehicle_value', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('vehicle_age', sa.Integer(), nullable=True),
        sa.Column('vehicle_mileage', sa.Float(), nullable=True),
        sa.Column('vehicle_registration', sa.String(length=50), nullable=True),
        sa.Column('driver_dob', sa.Date(), nullable=True),
        sa.Column('license_number', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('client_id')
    )

    op.create_table('client_housing',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('client_id', sa.UUID(), nullable=True),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('property_value', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('construction_year', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('client_id')
    )

    op.create_table('client_health',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('client_id', sa.UUID(), nullable=True),
        sa.Column('blood_group', sa.String(length=10), nullable=True),
        sa.Column('pre_existing_conditions', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('client_id')
    )

    op.create_table('client_travel',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('client_id', sa.UUID(), nullable=True),
        sa.Column('passport_number', sa.String(length=50), nullable=True),
        sa.Column('frequent_destinations', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('client_id')
    )

    op.create_table('client_life',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('client_id', sa.UUID(), nullable=True),
        sa.Column('beneficiaries', sa.String(length=500), nullable=True),
        sa.Column('smoking_status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('client_id')
    )

    # 7. Apply the schema changes to existing tables
    op.alter_column('clients', 'created_at', existing_type=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column('clients', 'updated_at', existing_type=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column('companies', 'created_at', existing_type=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column('companies', 'updated_at', existing_type=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column('policies', 'created_at', existing_type=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column('policies', 'updated_at', existing_type=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column('policy_types', 'created_at', existing_type=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column('policy_types', 'updated_at', existing_type=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column('quotes', 'created_at', existing_type=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column('quotes', 'updated_at', existing_type=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column('users', 'created_at', existing_type=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column('users', 'updated_at', existing_type=postgresql.TIMESTAMP(), nullable=True)


def downgrade() -> None:
    # Drop all Phase 7 tables
    op.drop_table('client_life')
    op.drop_table('client_travel')
    op.drop_table('client_health')
    op.drop_table('client_housing')
    op.drop_table('client_automobile')
    op.drop_index(op.f('ix_share_codes_code'), table_name='share_codes')
    op.drop_table('share_codes')
    op.drop_table('ml_models')
    op.drop_table('telematics_data')
    op.drop_table('loyalty_points')
    op.drop_table('referrals')
    op.drop_table('tickets')
    op.drop_table('claims')
    op.drop_table('inter_company_shares')
    op.drop_table('documents')

    # Revert schema changes (make nullable false again if that's what they were)
    # Caution: this might fail if there's null data
    op.alter_column('users', 'updated_at', existing_type=postgresql.TIMESTAMP(), nullable=False)
    op.alter_column('users', 'created_at', existing_type=postgresql.TIMESTAMP(), nullable=False)
    op.alter_column('quotes', 'updated_at', existing_type=postgresql.TIMESTAMP(), nullable=False)
    op.alter_column('quotes', 'created_at', existing_type=postgresql.TIMESTAMP(), nullable=False)
    op.alter_column('policy_types', 'updated_at', existing_type=postgresql.TIMESTAMP(), nullable=False)
    op.alter_column('policy_types', 'created_at', existing_type=postgresql.TIMESTAMP(), nullable=False)
    op.alter_column('policies', 'updated_at', existing_type=postgresql.TIMESTAMP(), nullable=False)
    op.alter_column('policies', 'created_at', existing_type=postgresql.TIMESTAMP(), nullable=False)
    op.alter_column('companies', 'updated_at', existing_type=postgresql.TIMESTAMP(), nullable=False)
    op.alter_column('companies', 'created_at', existing_type=postgresql.TIMESTAMP(), nullable=False)
    op.alter_column('clients', 'updated_at', existing_type=postgresql.TIMESTAMP(), nullable=False)
    op.alter_column('clients', 'created_at', existing_type=postgresql.TIMESTAMP(), nullable=False)
