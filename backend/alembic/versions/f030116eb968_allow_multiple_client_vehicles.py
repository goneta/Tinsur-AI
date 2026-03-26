"""allow multiple client vehicles

Revision ID: f030116eb968
Revises: b1c2d3e4f5g6
Create Date: 2026-02-05 01:17:20.757883+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f030116eb968'
down_revision = 'b1c2d3e4f5g6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table('client_automobile', 'client_automobile_old')

    op.create_table(
        'client_automobile',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('client_id', sa.String(length=36), nullable=True),
        sa.Column('vehicle_registration', sa.String(length=50), nullable=True),
        sa.Column('vehicle_make', sa.String(length=50), nullable=True),
        sa.Column('vehicle_model', sa.String(length=50), nullable=True),
        sa.Column('vehicle_year', sa.Integer(), nullable=True),
        sa.Column('vehicle_value', sa.Numeric(15, 2), nullable=True),
        sa.Column('vehicle_mileage', sa.Float(), nullable=True),
        sa.Column('engine_capacity_cc', sa.Integer(), nullable=True),
        sa.Column('fuel_type', sa.String(length=50), nullable=True),
        sa.Column('vehicle_usage', sa.String(length=50), nullable=True),
        sa.Column('seat_count', sa.Integer(), nullable=True),
        sa.Column('chassis_number', sa.String(length=100), nullable=True),
        sa.Column('vehicle_color', sa.String(length=50), nullable=True),
        sa.Column('country_of_registration', sa.String(length=100), nullable=True),
        sa.Column('registration_document_url', sa.String(length=500), nullable=True),
        sa.Column('parked_location', sa.String(length=100), nullable=True),
        sa.Column('vehicle_image_url', sa.String(length=500), nullable=True),
        sa.Column('driver_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('driver_dob', sa.Date(), nullable=True),
        sa.Column('license_number', sa.String(length=100), nullable=True),
        sa.Column('license_issue_date', sa.Date(), nullable=True),
        sa.Column('license_expiry_date', sa.Date(), nullable=True),
        sa.Column('license_category', sa.String(length=50), nullable=True),
        sa.Column('driving_experience_years', sa.Integer(), nullable=True),
        sa.Column('accident_count', sa.Integer(), nullable=True),
        sa.Column('claim_count', sa.Integer(), nullable=True),
        sa.Column('no_claim_bonus_status', sa.String(length=50), nullable=True),
        sa.Column('previous_insurer', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    columns = [
        'id',
        'client_id',
        'vehicle_registration',
        'vehicle_make',
        'vehicle_model',
        'vehicle_year',
        'vehicle_value',
        'vehicle_mileage',
        'engine_capacity_cc',
        'fuel_type',
        'vehicle_usage',
        'seat_count',
        'chassis_number',
        'vehicle_color',
        'country_of_registration',
        'registration_document_url',
        'parked_location',
        'vehicle_image_url',
        'driver_name',
        'last_name',
        'first_name',
        'driver_dob',
        'license_number',
        'license_issue_date',
        'license_expiry_date',
        'license_category',
        'driving_experience_years',
        'accident_count',
        'claim_count',
        'no_claim_bonus_status',
        'previous_insurer',
        'created_at',
        'updated_at',
    ]
    cols = ", ".join(columns)
    op.execute(f"INSERT INTO client_automobile ({cols}) SELECT {cols} FROM client_automobile_old")
    op.drop_table('client_automobile_old')


def downgrade() -> None:
    raise NotImplementedError("Downgrade not supported for client vehicle uniqueness migration")
