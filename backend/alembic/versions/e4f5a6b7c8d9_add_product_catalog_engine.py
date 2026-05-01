"""add product catalog engine

Revision ID: e4f5a6b7c8d9
Revises: a1b2c3d4e5f6, 9b4a7c2d1e0f
Create Date: 2026-05-02 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "e4f5a6b7c8d9"
down_revision = ("a1b2c3d4e5f6", "9b4a7c2d1e0f")
branch_labels = None
depends_on = None


def _uuid_type():
    bind = op.get_bind()
    return postgresql.UUID(as_uuid=True) if bind.dialect.name == "postgresql" else sa.CHAR(36)


def upgrade():
    uuid_type = _uuid_type()
    inspector = sa.inspect(op.get_bind())
    existing_tables = set(inspector.get_table_names())

    if "insurance_products" not in existing_tables:
        op.create_table(
            "insurance_products",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("code", sa.String(50), nullable=False),
            sa.Column("name", sa.String(150), nullable=False),
            sa.Column("product_line", sa.String(50), nullable=False),
            sa.Column("description", sa.Text()),
            sa.Column("status", sa.String(50), server_default="active"),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
            sa.Column("display_order", sa.Integer(), server_default="100"),
            sa.Column("metadata_json", sa.JSON()),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
            sa.UniqueConstraint("company_id", "code", name="uq_insurance_products_company_code"),
        )
        op.create_index("ix_insurance_products_company_id", "insurance_products", ["company_id"])
        op.create_index("ix_insurance_products_code", "insurance_products", ["code"])
        op.create_index("ix_insurance_products_product_line", "insurance_products", ["product_line"])
        op.create_index("ix_insurance_products_status", "insurance_products", ["status"])
        op.create_index("ix_insurance_products_is_active", "insurance_products", ["is_active"])

    if "insurance_product_versions" not in existing_tables:
        op.create_table(
            "insurance_product_versions",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("product_id", uuid_type, sa.ForeignKey("insurance_products.id", ondelete="CASCADE"), nullable=False),
            sa.Column("version", sa.String(50), nullable=False),
            sa.Column("status", sa.String(50), server_default="draft"),
            sa.Column("effective_from", sa.DateTime()),
            sa.Column("effective_to", sa.DateTime()),
            sa.Column("base_currency", sa.String(10), server_default="USD"),
            sa.Column("rating_strategy", sa.String(75), server_default="factor_table"),
            sa.Column("base_rate", sa.Numeric(10, 6), server_default="0"),
            sa.Column("minimum_premium", sa.Numeric(15, 2), server_default="0"),
            sa.Column("taxes_and_fees", sa.JSON()),
            sa.Column("configuration", sa.JSON()),
            sa.Column("approved_by_id", uuid_type, sa.ForeignKey("users.id")),
            sa.Column("created_by_id", uuid_type, sa.ForeignKey("users.id")),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
            sa.UniqueConstraint("company_id", "product_id", "version", name="uq_product_versions_company_product_version"),
        )
        op.create_index("ix_insurance_product_versions_company_id", "insurance_product_versions", ["company_id"])
        op.create_index("ix_insurance_product_versions_product_id", "insurance_product_versions", ["product_id"])
        op.create_index("ix_insurance_product_versions_status", "insurance_product_versions", ["status"])

    if "product_coverages" not in existing_tables:
        op.create_table(
            "product_coverages",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("product_version_id", uuid_type, sa.ForeignKey("insurance_product_versions.id", ondelete="CASCADE"), nullable=False),
            sa.Column("code", sa.String(75), nullable=False),
            sa.Column("name", sa.String(150), nullable=False),
            sa.Column("coverage_type", sa.String(75), nullable=False),
            sa.Column("description", sa.Text()),
            sa.Column("is_required", sa.Boolean(), server_default=sa.text("false")),
            sa.Column("default_limit", sa.Numeric(15, 2)),
            sa.Column("minimum_limit", sa.Numeric(15, 2)),
            sa.Column("maximum_limit", sa.Numeric(15, 2)),
            sa.Column("default_deductible", sa.Numeric(15, 2)),
            sa.Column("exclusions", sa.JSON()),
            sa.Column("conditions", sa.JSON()),
            sa.Column("display_order", sa.Integer(), server_default="100"),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
            sa.UniqueConstraint("product_version_id", "code", name="uq_product_coverages_version_code"),
        )
        op.create_index("ix_product_coverages_company_id", "product_coverages", ["company_id"])
        op.create_index("ix_product_coverages_product_version_id", "product_coverages", ["product_version_id"])
        op.create_index("ix_product_coverages_code", "product_coverages", ["code"])

    if "product_coverage_options" not in existing_tables:
        op.create_table(
            "product_coverage_options",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("coverage_id", uuid_type, sa.ForeignKey("product_coverages.id", ondelete="CASCADE"), nullable=False),
            sa.Column("code", sa.String(75), nullable=False),
            sa.Column("label", sa.String(150), nullable=False),
            sa.Column("option_type", sa.String(50), server_default="limit"),
            sa.Column("limit_amount", sa.Numeric(15, 2)),
            sa.Column("deductible_amount", sa.Numeric(15, 2)),
            sa.Column("premium_delta", sa.Numeric(15, 2), server_default="0"),
            sa.Column("rate_multiplier", sa.Numeric(10, 6), server_default="1"),
            sa.Column("configuration", sa.JSON()),
            sa.Column("is_default", sa.Boolean(), server_default=sa.text("false")),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
            sa.Column("display_order", sa.Integer(), server_default="100"),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
            sa.UniqueConstraint("coverage_id", "code", name="uq_product_coverage_options_coverage_code"),
        )
        op.create_index("ix_product_coverage_options_company_id", "product_coverage_options", ["company_id"])
        op.create_index("ix_product_coverage_options_coverage_id", "product_coverage_options", ["coverage_id"])
        op.create_index("ix_product_coverage_options_code", "product_coverage_options", ["code"])

    if "product_rating_factors" not in existing_tables:
        op.create_table(
            "product_rating_factors",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("product_version_id", uuid_type, sa.ForeignKey("insurance_product_versions.id", ondelete="CASCADE"), nullable=False),
            sa.Column("code", sa.String(100), nullable=False),
            sa.Column("name", sa.String(150), nullable=False),
            sa.Column("factor_type", sa.String(75), nullable=False),
            sa.Column("applies_to", sa.String(75), nullable=False),
            sa.Column("input_path", sa.String(255), nullable=False),
            sa.Column("operator", sa.String(50), server_default="equals"),
            sa.Column("value", sa.String(255)),
            sa.Column("factor", sa.Numeric(10, 6), server_default="1"),
            sa.Column("amount", sa.Numeric(15, 2), server_default="0"),
            sa.Column("priority", sa.Integer(), server_default="100"),
            sa.Column("configuration", sa.JSON()),
            sa.Column("reason_code", sa.String(100)),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
            sa.UniqueConstraint("product_version_id", "code", name="uq_product_rating_factors_version_code"),
        )
        op.create_index("ix_product_rating_factors_company_id", "product_rating_factors", ["company_id"])
        op.create_index("ix_product_rating_factors_product_version_id", "product_rating_factors", ["product_version_id"])
        op.create_index("ix_product_rating_factors_code", "product_rating_factors", ["code"])

    if "product_underwriting_rules" not in existing_tables:
        op.create_table(
            "product_underwriting_rules",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("product_version_id", uuid_type, sa.ForeignKey("insurance_product_versions.id", ondelete="CASCADE"), nullable=False),
            sa.Column("code", sa.String(100), nullable=False),
            sa.Column("name", sa.String(150), nullable=False),
            sa.Column("rule_type", sa.String(75), server_default="eligibility"),
            sa.Column("decision_effect", sa.String(50), server_default="refer"),
            sa.Column("condition", sa.JSON()),
            sa.Column("message", sa.String(500)),
            sa.Column("authority_level", sa.String(75)),
            sa.Column("priority", sa.Integer(), server_default="100"),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
            sa.UniqueConstraint("product_version_id", "code", name="uq_product_underwriting_rules_version_code"),
        )
        op.create_index("ix_product_underwriting_rules_company_id", "product_underwriting_rules", ["company_id"])
        op.create_index("ix_product_underwriting_rules_product_version_id", "product_underwriting_rules", ["product_version_id"])
        op.create_index("ix_product_underwriting_rules_code", "product_underwriting_rules", ["code"])

    if "product_quote_wizard_schemas" not in existing_tables:
        op.create_table(
            "product_quote_wizard_schemas",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("product_version_id", uuid_type, sa.ForeignKey("insurance_product_versions.id", ondelete="CASCADE"), nullable=False),
            sa.Column("channel", sa.String(50), server_default="portal"),
            sa.Column("schema_version", sa.String(50), server_default="1.0"),
            sa.Column("title", sa.String(150), nullable=False),
            sa.Column("steps", sa.JSON()),
            sa.Column("validation_schema", sa.JSON()),
            sa.Column("ui_schema", sa.JSON()),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
            sa.UniqueConstraint("product_version_id", "channel", "schema_version", name="uq_quote_wizard_schema_version_channel"),
        )
        op.create_index("ix_product_quote_wizard_schemas_company_id", "product_quote_wizard_schemas", ["company_id"])
        op.create_index("ix_product_quote_wizard_schemas_product_version_id", "product_quote_wizard_schemas", ["product_version_id"])


def downgrade():
    inspector = sa.inspect(op.get_bind())
    existing_tables = set(inspector.get_table_names())
    for table_name in (
        "product_quote_wizard_schemas",
        "product_underwriting_rules",
        "product_rating_factors",
        "product_coverage_options",
        "product_coverages",
        "insurance_product_versions",
        "insurance_products",
    ):
        if table_name in existing_tables:
            op.drop_table(table_name)
