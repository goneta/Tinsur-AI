"""add product specific detail models

Revision ID: f6a7b8c9d0e1
Revises: e4f5a6b7c8d9
Create Date: 2026-05-02 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "f6a7b8c9d0e1"
down_revision = "e4f5a6b7c8d9"
branch_labels = None
depends_on = None


def _uuid_type():
    bind = op.get_bind()
    return postgresql.UUID(as_uuid=True) if bind.dialect.name == "postgresql" else sa.CHAR(36)


def upgrade():
    uuid_type = _uuid_type()
    inspector = sa.inspect(op.get_bind())
    existing_tables = set(inspector.get_table_names())

    if "product_application_details" not in existing_tables:
        op.create_table(
            "product_application_details",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("quote_id", uuid_type, sa.ForeignKey("quotes.id", ondelete="CASCADE"), nullable=False),
            sa.Column("product_version_id", uuid_type, sa.ForeignKey("insurance_product_versions.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("quote_wizard_schema_id", uuid_type, sa.ForeignKey("product_quote_wizard_schemas.id", ondelete="SET NULL"), nullable=True),
            sa.Column("schema_version", sa.String(50), nullable=False, server_default="1.0"),
            sa.Column("validation_schema_ref", sa.String(255), nullable=True),
            sa.Column("application_data", sa.JSON(), nullable=False),
            sa.Column("validation_status", sa.String(50), nullable=False, server_default="pending"),
            sa.Column("validation_errors", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
            sa.UniqueConstraint("quote_id", name="uq_product_application_details_quote_id"),
        )
        op.create_index("ix_product_application_details_company_id", "product_application_details", ["company_id"])
        op.create_index("ix_product_application_details_quote_id", "product_application_details", ["quote_id"])
        op.create_index("ix_product_application_details_product_version_id", "product_application_details", ["product_version_id"])
        op.create_index("ix_product_application_details_quote_wizard_schema_id", "product_application_details", ["quote_wizard_schema_id"])
        op.create_index("ix_product_application_details_schema_version", "product_application_details", ["schema_version"])
        op.create_index("ix_product_application_details_validation_status", "product_application_details", ["validation_status"])

    if "product_rating_snapshots" not in existing_tables:
        op.create_table(
            "product_rating_snapshots",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("policy_id", uuid_type, sa.ForeignKey("policies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("product_version_id", uuid_type, sa.ForeignKey("insurance_product_versions.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("schema_version", sa.String(50), nullable=False, server_default="1.0"),
            sa.Column("validation_schema_ref", sa.String(255), nullable=True),
            sa.Column("rating_data", sa.JSON(), nullable=False),
            sa.Column("validation_status", sa.String(50), nullable=False, server_default="pending"),
            sa.Column("validation_errors", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
            sa.UniqueConstraint("policy_id", name="uq_product_rating_snapshots_policy_id"),
        )
        op.create_index("ix_product_rating_snapshots_company_id", "product_rating_snapshots", ["company_id"])
        op.create_index("ix_product_rating_snapshots_policy_id", "product_rating_snapshots", ["policy_id"])
        op.create_index("ix_product_rating_snapshots_product_version_id", "product_rating_snapshots", ["product_version_id"])
        op.create_index("ix_product_rating_snapshots_schema_version", "product_rating_snapshots", ["schema_version"])
        op.create_index("ix_product_rating_snapshots_validation_status", "product_rating_snapshots", ["validation_status"])

    if "product_claim_details" not in existing_tables:
        op.create_table(
            "product_claim_details",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("claim_id", uuid_type, sa.ForeignKey("claims.id", ondelete="CASCADE"), nullable=False),
            sa.Column("product_version_id", uuid_type, sa.ForeignKey("insurance_product_versions.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("schema_version", sa.String(50), nullable=False, server_default="1.0"),
            sa.Column("validation_schema_ref", sa.String(255), nullable=True),
            sa.Column("claim_data", sa.JSON(), nullable=False),
            sa.Column("validation_status", sa.String(50), nullable=False, server_default="pending"),
            sa.Column("validation_errors", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
            sa.UniqueConstraint("claim_id", name="uq_product_claim_details_claim_id"),
        )
        op.create_index("ix_product_claim_details_company_id", "product_claim_details", ["company_id"])
        op.create_index("ix_product_claim_details_claim_id", "product_claim_details", ["claim_id"])
        op.create_index("ix_product_claim_details_product_version_id", "product_claim_details", ["product_version_id"])
        op.create_index("ix_product_claim_details_schema_version", "product_claim_details", ["schema_version"])
        op.create_index("ix_product_claim_details_validation_status", "product_claim_details", ["validation_status"])


def downgrade():
    inspector = sa.inspect(op.get_bind())
    existing_tables = set(inspector.get_table_names())
    for table_name in (
        "product_claim_details",
        "product_rating_snapshots",
        "product_application_details",
    ):
        if table_name in existing_tables:
            op.drop_table(table_name)
