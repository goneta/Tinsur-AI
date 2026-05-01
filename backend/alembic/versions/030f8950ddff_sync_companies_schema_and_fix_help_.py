"""sync companies schema and fix help guide models

Revision ID: 030f8950ddff
Revises: 002b_accidents
Create Date: 2026-04-05 21:51:26.149636+00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '030f8950ddff'
down_revision = '002b_accidents'
branch_labels = None
depends_on = None


def _col_exists(table, column):
    """Check if a column already exists (safe for re-runs)."""
    from sqlalchemy import inspect as sa_inspect
    bind = op.get_bind()
    inspector = sa_inspect(bind)
    columns = [c["name"] for c in inspector.get_columns(table)]
    return column in columns


def upgrade() -> None:
    # ── Companies: add columns that the model expects but the DB is missing ──
    new_company_cols = {
        "subdomain": sa.Column("subdomain", sa.String(100), unique=True),
        "email": sa.Column("email", sa.String(255)),
        "phone": sa.Column("phone", sa.String(50)),
        "address": sa.Column("address", sa.Text()),
        "registration_number": sa.Column("registration_number", sa.String(100)),
        "system_registration_number": sa.Column("system_registration_number", sa.String(50), unique=True),
        "bank_details": sa.Column("bank_details", sa.JSON()),
        "mobile_money_accounts": sa.Column("mobile_money_accounts", sa.JSON()),
        "apr_percent": sa.Column("apr_percent", sa.Float(), server_default="0"),
        "arrangement_fee": sa.Column("arrangement_fee", sa.Numeric(15, 2), server_default="0"),
        "extra_fee": sa.Column("extra_fee", sa.Numeric(15, 2), server_default="0"),
        "currency": sa.Column("currency", sa.String(10), server_default="USD"),
        "country": sa.Column("country", sa.String(100)),
        "timezone": sa.Column("timezone", sa.String(50), server_default="UTC"),
        "government_tax_percent": sa.Column("government_tax_percent", sa.Float(), server_default="0"),
        "admin_fee": sa.Column("admin_fee", sa.Numeric(15, 2), server_default="0"),
        "admin_fee_percent": sa.Column("admin_fee_percent", sa.Float(), server_default="0"),
        "admin_discount_percent": sa.Column("admin_discount_percent", sa.Float(), server_default="0"),
        "is_active": sa.Column("is_active", sa.Boolean(), server_default="true"),
        "logo_url": sa.Column("logo_url", sa.String()),
        "primary_color": sa.Column("primary_color", sa.String(10)),
        "secondary_color": sa.Column("secondary_color", sa.String(10)),
        "theme_colors": sa.Column("theme_colors", sa.String()),
        "features": sa.Column("features", sa.JSON()),
        "ai_plan": sa.Column("ai_plan", sa.String(20), server_default="CREDIT"),
        "ai_api_key_encrypted": sa.Column("ai_api_key_encrypted", sa.String(500)),
        "ai_credits_balance": sa.Column("ai_credits_balance", sa.Float(), server_default="100"),
    }

    for col_name, col_obj in new_company_cols.items():
        if not _col_exists("companies", col_name):
            op.add_column("companies", col_obj)

    # Back-fill subdomain for any existing rows that have it NULL
    op.execute(
        "UPDATE companies SET subdomain = LOWER(REPLACE(name, ' ', '-')) "
        "WHERE subdomain IS NULL"
    )

    # ── Help-guide tables (new) ──
    # These use GUID (UUID) columns to match the rest of the app.
    from app.core.guid import GUID

    if not _table_exists("help_guides"):
        op.create_table(
            "help_guides",
            sa.Column("id", GUID(), primary_key=True),
            sa.Column("title", sa.String(), index=True),
            sa.Column("description", sa.Text()),
            sa.Column("content", sa.Text()),
            sa.Column("guide_type", sa.Enum("client", "admin", "insurance_company", name="guidetype"), index=True),
            sa.Column("section", sa.Enum(
                "getting_started", "client_management", "quote_creation",
                "policy_management", "reports", "user_management",
                "security", "integrations", "troubleshooting",
                name="guidesection"), index=True, nullable=True),
            sa.Column("display_order", sa.Integer(), server_default="0"),
            sa.Column("is_active", sa.Boolean(), server_default="true"),
            sa.Column("tags", sa.String(), nullable=True),
            sa.Column("estimated_read_time", sa.Integer(), server_default="5"),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
        )

    if not _table_exists("guide_completions"):
        op.create_table(
            "guide_completions",
            sa.Column("id", GUID(), primary_key=True),
            sa.Column("user_id", GUID(), sa.ForeignKey("users.id"), index=True),
            sa.Column("guide_id", GUID(), sa.ForeignKey("help_guides.id"), index=True),
            sa.Column("completed_at", sa.DateTime()),
            sa.Column("created_at", sa.DateTime()),
        )

    if not _table_exists("guide_accesses"):
        op.create_table(
            "guide_accesses",
            sa.Column("id", GUID(), primary_key=True),
            sa.Column("user_id", GUID(), sa.ForeignKey("users.id"), index=True, nullable=True),
            sa.Column("guide_id", GUID(), sa.ForeignKey("help_guides.id"), index=True),
            sa.Column("section_accessed", sa.String(), nullable=True),
            sa.Column("accessed_at", sa.DateTime(), index=True),
            sa.Column("time_spent_seconds", sa.Integer(), server_default="0"),
            sa.Column("created_at", sa.DateTime()),
        )

    if not _table_exists("onboarding_status"):
        op.create_table(
            "onboarding_status",
            sa.Column("id", GUID(), primary_key=True),
            sa.Column("user_id", GUID(), sa.ForeignKey("users.id"), unique=True, index=True),
            sa.Column("current_step", sa.Integer(), server_default="0"),
            sa.Column("completed", sa.Boolean(), server_default="false"),
            sa.Column("skipped", sa.Boolean(), server_default="false"),
            sa.Column("last_accessed_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
        )


def downgrade() -> None:
    # Drop help-guide tables
    op.drop_table("onboarding_status")
    op.drop_table("guide_accesses")
    op.drop_table("guide_completions")
    op.drop_table("help_guides")
    op.execute("DROP TYPE IF EXISTS guidesection")
    op.execute("DROP TYPE IF EXISTS guidetype")

    # Remove added company columns (only the ones this migration adds)
    cols_to_drop = [
        "subdomain", "email", "phone", "address",
        "registration_number", "system_registration_number",
        "bank_details", "mobile_money_accounts",
        "apr_percent", "arrangement_fee", "extra_fee",
        "currency", "country", "timezone",
        "government_tax_percent", "admin_fee", "admin_fee_percent",
        "admin_discount_percent", "is_active", "logo_url",
        "primary_color", "secondary_color", "theme_colors",
        "features", "ai_plan", "ai_api_key_encrypted", "ai_credits_balance",
    ]
    for col in cols_to_drop:
        op.drop_column("companies", col)


def _table_exists(table_name):
    """Check if a table already exists."""
    from sqlalchemy import inspect as sa_inspect
    bind = op.get_bind()
    inspector = sa_inspect(bind)
    return table_name in inspector.get_table_names()
