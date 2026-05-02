"""add production launch control layer

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-05-02 13:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "a7b8c9d0e1f2"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


def _uuid_type():
    bind = op.get_bind()
    return postgresql.UUID(as_uuid=True) if bind.dialect.name == "postgresql" else sa.CHAR(36)


def upgrade():
    uuid_type = _uuid_type()
    inspector = sa.inspect(op.get_bind())
    existing_tables = set(inspector.get_table_names())

    if "consequential_action_policies" not in existing_tables:
        op.create_table(
            "consequential_action_policies",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("action_key", sa.String(100), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("required_roles", sa.JSON(), nullable=False),
            sa.Column("requires_approval", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("requires_document_template_approval", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("requires_payment_live_mode", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("audit_required", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("production_only_rules", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
            sa.UniqueConstraint("action_key", name="uq_consequential_action_policies_action_key"),
        )
        op.create_index("ix_consequential_action_policies_action_key", "consequential_action_policies", ["action_key"])
        op.create_index("ix_consequential_action_policies_requires_approval", "consequential_action_policies", ["requires_approval"])
        op.create_index("ix_consequential_action_policies_enabled", "consequential_action_policies", ["enabled"])

    if "approval_requests" not in existing_tables:
        op.create_table(
            "approval_requests",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("action_policy_id", uuid_type, sa.ForeignKey("consequential_action_policies.id", ondelete="RESTRICT"), nullable=True),
            sa.Column("action_key", sa.String(100), nullable=False),
            sa.Column("target_type", sa.String(100), nullable=False),
            sa.Column("target_id", sa.String(100), nullable=False),
            sa.Column("requested_by_id", uuid_type, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
            sa.Column("reason", sa.Text(), nullable=True),
            sa.Column("request_payload", sa.JSON(), nullable=False),
            sa.Column("required_roles", sa.JSON(), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.Column("executed_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
        )
        for column in ("company_id", "action_policy_id", "action_key", "target_type", "target_id", "requested_by_id", "status", "expires_at"):
            op.create_index(f"ix_approval_requests_{column}", "approval_requests", [column])

    if "approval_decisions" not in existing_tables:
        op.create_table(
            "approval_decisions",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("approval_request_id", uuid_type, sa.ForeignKey("approval_requests.id", ondelete="CASCADE"), nullable=False),
            sa.Column("decided_by_id", uuid_type, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("decision", sa.String(50), nullable=False),
            sa.Column("decision_reason", sa.Text(), nullable=True),
            sa.Column("decision_payload", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime()),
        )
        op.create_index("ix_approval_decisions_approval_request_id", "approval_decisions", ["approval_request_id"])
        op.create_index("ix_approval_decisions_decided_by_id", "approval_decisions", ["decided_by_id"])
        op.create_index("ix_approval_decisions_decision", "approval_decisions", ["decision"])

    if "production_audit_events" not in existing_tables:
        op.create_table(
            "production_audit_events",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("company_id", uuid_type, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            sa.Column("actor_id", uuid_type, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("approval_request_id", uuid_type, sa.ForeignKey("approval_requests.id", ondelete="SET NULL"), nullable=True),
            sa.Column("action_key", sa.String(100), nullable=False),
            sa.Column("event_type", sa.String(100), nullable=False),
            sa.Column("target_type", sa.String(100), nullable=False),
            sa.Column("target_id", sa.String(100), nullable=False),
            sa.Column("decision", sa.String(50), nullable=False),
            sa.Column("reason", sa.Text(), nullable=True),
            sa.Column("payload_hash", sa.String(128), nullable=True),
            sa.Column("before_hash", sa.String(128), nullable=True),
            sa.Column("after_hash", sa.String(128), nullable=True),
            sa.Column("correlation_id", sa.String(100), nullable=True),
            sa.Column("environment", sa.String(50), nullable=False, server_default="unknown"),
            sa.Column("event_metadata", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime()),
        )
        for column in ("company_id", "actor_id", "approval_request_id", "action_key", "event_type", "target_type", "target_id", "decision", "correlation_id", "environment", "created_at"):
            op.create_index(f"ix_production_audit_events_{column}", "production_audit_events", [column])

    if "document_template_approvals" not in existing_tables:
        op.create_table(
            "document_template_approvals",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("template_key", sa.String(100), nullable=False),
            sa.Column("version", sa.String(50), nullable=False, server_default="1.0"),
            sa.Column("jurisdiction", sa.String(100), nullable=False, server_default="default"),
            sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
            sa.Column("approved_by_id", uuid_type, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("approved_at", sa.DateTime(), nullable=True),
            sa.Column("approval_notes", sa.Text(), nullable=True),
            sa.Column("content_hash", sa.String(128), nullable=True),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
            sa.UniqueConstraint("template_key", "version", "jurisdiction", name="uq_document_template_approval_version"),
        )
        for column in ("template_key", "version", "jurisdiction", "status", "approved_by_id", "content_hash"):
            op.create_index(f"ix_document_template_approvals_{column}", "document_template_approvals", [column])

    if "launch_readiness_checks" not in existing_tables:
        op.create_table(
            "launch_readiness_checks",
            sa.Column("id", uuid_type, primary_key=True),
            sa.Column("check_key", sa.String(100), nullable=False),
            sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
            sa.Column("severity", sa.String(50), nullable=False, server_default="blocking"),
            sa.Column("details", sa.JSON(), nullable=False),
            sa.Column("last_checked_at", sa.DateTime()),
            sa.Column("created_at", sa.DateTime()),
            sa.Column("updated_at", sa.DateTime()),
            sa.UniqueConstraint("check_key", name="uq_launch_readiness_checks_check_key"),
        )
        for column in ("check_key", "status", "severity", "last_checked_at"):
            op.create_index(f"ix_launch_readiness_checks_{column}", "launch_readiness_checks", [column])


def downgrade():
    inspector = sa.inspect(op.get_bind())
    existing_tables = set(inspector.get_table_names())
    for table_name in (
        "launch_readiness_checks",
        "document_template_approvals",
        "production_audit_events",
        "approval_decisions",
        "approval_requests",
        "consequential_action_policies",
    ):
        if table_name in existing_tables:
            op.drop_table(table_name)
