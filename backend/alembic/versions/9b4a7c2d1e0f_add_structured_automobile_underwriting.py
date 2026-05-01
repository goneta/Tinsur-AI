"""add structured automobile underwriting tables

Revision ID: 9b4a7c2d1e0f
Revises: f030116eb968
Create Date: 2026-05-01 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "9b4a7c2d1e0f"
down_revision = "f030116eb968"
branch_labels = None
depends_on = None


def _uuid_type():
    bind = op.get_bind()
    return postgresql.UUID(as_uuid=True) if bind.dialect.name == "postgresql" else sa.CHAR(36)


def upgrade():
    uuid_type = _uuid_type()
    inspector = sa.inspect(op.get_bind())
    existing_tables = set(inspector.get_table_names())

    if "vehicles" not in existing_tables:
        op.create_table(
            "vehicles",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("client_id", uuid_type, sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False),
            sa.Column("client_automobile_id", uuid_type, sa.ForeignKey("client_automobile.id", ondelete="SET NULL"), nullable=True),
            sa.Column("registration_number", sa.String(50)),
            sa.Column("vin", sa.String(100)),
            sa.Column("make", sa.String(100), nullable=False),
            sa.Column("model", sa.String(100), nullable=False),
            sa.Column("variant", sa.String(100)),
            sa.Column("year", sa.Integer(), nullable=False),
            sa.Column("body_type", sa.String(75)),
            sa.Column("fuel_type", sa.String(50)),
            sa.Column("transmission", sa.String(50)),
            sa.Column("engine_size_cc", sa.Integer()),
            sa.Column("seat_count", sa.Integer()),
            sa.Column("market_value", sa.Numeric(15, 2), nullable=False),
            sa.Column("annual_mileage", sa.Integer()),
            sa.Column("usage_class", sa.String(75), nullable=False),
            sa.Column("garaging_postcode", sa.String(30)),
            sa.Column("garaging_region", sa.String(100)),
            sa.Column("overnight_parking", sa.String(100)),
            sa.Column("security_devices", sa.JSON()),
            sa.Column("modifications", sa.JSON()),
            sa.Column("imported", sa.Boolean(), server_default=sa.text("false")),
            sa.Column("prior_damage", sa.Boolean(), server_default=sa.text("false")),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
        )
        op.create_index("ix_vehicles_company_id", "vehicles", ["company_id"])
        op.create_index("ix_vehicles_client_id", "vehicles", ["client_id"])
        op.create_index("ix_vehicles_registration_number", "vehicles", ["registration_number"])
        op.create_index("ix_vehicles_vin", "vehicles", ["vin"])

    if "drivers" not in existing_tables:
        op.create_table(
            "drivers",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("client_id", uuid_type, sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False),
            sa.Column("vehicle_id", uuid_type, sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=True),
            sa.Column("client_driver_id", uuid_type, sa.ForeignKey("client_drivers.id", ondelete="SET NULL"), nullable=True),
            sa.Column("is_primary", sa.Boolean(), server_default=sa.text("false")),
            sa.Column("first_name", sa.String(100), nullable=False),
            sa.Column("last_name", sa.String(100), nullable=False),
            sa.Column("date_of_birth", sa.Date(), nullable=False),
            sa.Column("licence_type", sa.String(75)),
            sa.Column("licence_issue_date", sa.Date()),
            sa.Column("years_licensed", sa.Integer(), server_default="0"),
            sa.Column("occupation", sa.String(150)),
            sa.Column("marital_status", sa.String(50)),
            sa.Column("address_postcode", sa.String(30)),
            sa.Column("address_region", sa.String(100)),
            sa.Column("no_claim_discount_years", sa.Integer(), server_default="0"),
            sa.Column("no_claim_discount_protected", sa.Boolean(), server_default=sa.text("false")),
            sa.Column("previous_insurer", sa.String(150)),
            sa.Column("cancellation_or_refusal_history", sa.Boolean(), server_default=sa.text("false")),
            sa.Column("relationship_to_policyholder", sa.String(75)),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
        )
        op.create_index("ix_drivers_company_id", "drivers", ["company_id"])
        op.create_index("ix_drivers_client_id", "drivers", ["client_id"])
        op.create_index("ix_drivers_vehicle_id", "drivers", ["vehicle_id"])

    if "driver_claim_history" not in existing_tables:
        op.create_table(
            "driver_claim_history",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("driver_id", uuid_type, sa.ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False),
            sa.Column("claim_date", sa.Date()),
            sa.Column("claim_type", sa.String(100)),
            sa.Column("amount", sa.Numeric(15, 2), server_default="0"),
            sa.Column("at_fault", sa.Boolean(), server_default=sa.text("false")),
            sa.Column("settled", sa.Boolean(), server_default=sa.text("true")),
            sa.Column("description", sa.Text()),
            sa.Column("created_at", sa.DateTime()),
        )
        op.create_index("ix_driver_claim_history_driver_id", "driver_claim_history", ["driver_id"])

    if "driver_conviction_history" not in existing_tables:
        op.create_table(
            "driver_conviction_history",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("driver_id", uuid_type, sa.ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False),
            sa.Column("conviction_date", sa.Date()),
            sa.Column("code", sa.String(50)),
            sa.Column("description", sa.Text()),
            sa.Column("points", sa.Integer(), server_default="0"),
            sa.Column("severity", sa.String(50), server_default="minor"),
            sa.Column("created_at", sa.DateTime()),
        )
        op.create_index("ix_driver_conviction_history_driver_id", "driver_conviction_history", ["driver_id"])

    if "vehicle_risk_profiles" not in existing_tables:
        op.create_table(
            "vehicle_risk_profiles",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("vehicle_id", uuid_type, sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, unique=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("risk_group", sa.String(75), server_default="standard"),
            sa.Column("risk_score", sa.Numeric(5, 2), server_default="0"),
            sa.Column("factors", sa.JSON()),
            sa.Column("reason_codes", sa.JSON()),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
        )
        op.create_index("ix_vehicle_risk_profiles_company_id", "vehicle_risk_profiles", ["company_id"])

    if "underwriting_rule_sets" not in existing_tables:
        op.create_table(
            "underwriting_rule_sets",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(150), nullable=False),
            sa.Column("version", sa.String(50), nullable=False),
            sa.Column("status", sa.String(50), server_default="active"),
            sa.Column("effective_from", sa.DateTime()),
            sa.Column("effective_to", sa.DateTime()),
            sa.Column("default_base_rate", sa.Numeric(8, 5), server_default="0.045"),
            sa.Column("configuration", sa.JSON()),
            sa.Column("created_by_id", uuid_type, sa.ForeignKey("users.id")),
            sa.Column("approved_by_id", uuid_type, sa.ForeignKey("users.id")),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
            sa.UniqueConstraint("company_id", "version", name="uq_underwriting_rule_sets_company_version"),
        )
        op.create_index("ix_underwriting_rule_sets_company_id", "underwriting_rule_sets", ["company_id"])

    if "underwriting_rules" not in existing_tables:
        op.create_table(
            "underwriting_rules",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("rule_set_id", uuid_type, sa.ForeignKey("underwriting_rule_sets.id", ondelete="CASCADE"), nullable=False),
            sa.Column("code", sa.String(100), nullable=False),
            sa.Column("name", sa.String(150), nullable=False),
            sa.Column("category", sa.String(75), nullable=False),
            sa.Column("priority", sa.Integer(), server_default="100"),
            sa.Column("decision_effect", sa.String(50), server_default="rate"),
            sa.Column("condition", sa.JSON()),
            sa.Column("rate_effect", sa.JSON()),
            sa.Column("message", sa.String(500)),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
        )
        op.create_index("ix_underwriting_rules_rule_set_id", "underwriting_rules", ["rule_set_id"])
        op.create_index("ix_underwriting_rules_code", "underwriting_rules", ["code"])

    if "underwriting_decisions" not in existing_tables:
        op.create_table(
            "underwriting_decisions",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("quote_id", uuid_type, sa.ForeignKey("quotes.id", ondelete="CASCADE"), nullable=True),
            sa.Column("rule_set_id", uuid_type, sa.ForeignKey("underwriting_rule_sets.id", ondelete="SET NULL"), nullable=True),
            sa.Column("decision", sa.String(50), nullable=False),
            sa.Column("status", sa.String(50), server_default="final"),
            sa.Column("base_premium", sa.Numeric(15, 2), server_default="0"),
            sa.Column("final_premium", sa.Numeric(15, 2), server_default="0"),
            sa.Column("risk_score", sa.Numeric(5, 2), server_default="0"),
            sa.Column("breakdown", sa.JSON()),
            sa.Column("referral_reasons", sa.JSON()),
            sa.Column("decline_reasons", sa.JSON()),
            sa.Column("required_documents", sa.JSON()),
            sa.Column("warnings", sa.JSON()),
            sa.Column("assumptions", sa.JSON()),
            sa.Column("rule_matches", sa.JSON()),
            sa.Column("input_snapshot", sa.JSON()),
            sa.Column("decided_at", sa.DateTime()),
            sa.Column("created_at", sa.DateTime()),
        )
        op.create_index("ix_underwriting_decisions_company_id", "underwriting_decisions", ["company_id"])
        op.create_index("ix_underwriting_decisions_quote_id", "underwriting_decisions", ["quote_id"])

    if "quote_underwriting_snapshots" not in existing_tables:
        op.create_table(
            "quote_underwriting_snapshots",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("quote_id", uuid_type, sa.ForeignKey("quotes.id", ondelete="CASCADE"), nullable=False, unique=True),
            sa.Column("underwriting_decision_id", uuid_type, sa.ForeignKey("underwriting_decisions.id", ondelete="SET NULL"), nullable=True),
            sa.Column("rule_set_id", uuid_type, sa.ForeignKey("underwriting_rule_sets.id", ondelete="SET NULL"), nullable=True),
            sa.Column("normalized_payload", sa.JSON()),
            sa.Column("decision_snapshot", sa.JSON()),
            sa.Column("premium_breakdown", sa.JSON()),
            sa.Column("policy_ready_payload", sa.JSON()),
            sa.Column("valid_until", sa.DateTime()),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
        )
        op.create_index("ix_quote_underwriting_snapshots_company_id", "quote_underwriting_snapshots", ["company_id"])
        op.create_index("ix_quote_underwriting_snapshots_quote_id", "quote_underwriting_snapshots", ["quote_id"])


def downgrade():
    for table in [
        "quote_underwriting_snapshots",
        "underwriting_decisions",
        "underwriting_rules",
        "underwriting_rule_sets",
        "vehicle_risk_profiles",
        "driver_conviction_history",
        "driver_claim_history",
        "drivers",
        "vehicles",
    ]:
        op.drop_table(table)
