"""add document templates and document links

Revision ID: b1c2d3e4f5g6
Revises: a3c1b9d4c5e7
Create Date: 2026-02-03 06:30:00.000000
"""

from alembic import op
import sqlalchemy as sa
from app.core.guid import GUID
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "b1c2d3e4f5g6"
down_revision = "a3c1b9d4c5e7"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if "document_templates" not in inspector.get_table_names():
        op.create_table(
            "document_templates",
            sa.Column("id", GUID(), primary_key=True, nullable=False),
            sa.Column("code", sa.String(length=150), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("language", sa.String(length=10), nullable=True),
            sa.Column("template_html", sa.Text(), nullable=False),
            sa.Column("placeholders", sa.JSON(), nullable=True),
            sa.Column("source_path", sa.String(length=500), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
    if "ix_document_templates_code" not in [idx["name"] for idx in inspector.get_indexes("document_templates")]:
        op.create_index("ix_document_templates_code", "document_templates", ["code"], unique=True)

    with op.batch_alter_table("documents") as batch_op:
        existing_cols = {col["name"] for col in inspector.get_columns("documents")}
        if "policy_id" not in existing_cols:
            batch_op.add_column(sa.Column("policy_id", GUID(), nullable=True))
        if "client_id" not in existing_cols:
            batch_op.add_column(sa.Column("client_id", GUID(), nullable=True))
        if "template_id" not in existing_cols:
            batch_op.add_column(sa.Column("template_id", GUID(), nullable=True))
        if "verification_code" not in existing_cols:
            batch_op.add_column(sa.Column("verification_code", sa.String(length=16), nullable=True))
        if "qr_payload" not in existing_cols:
            batch_op.add_column(sa.Column("qr_payload", sa.Text(), nullable=True))

        existing_indexes = {idx["name"] for idx in inspector.get_indexes("documents")}
        if "ix_documents_policy_id" not in existing_indexes:
            batch_op.create_index("ix_documents_policy_id", ["policy_id"])
        if "ix_documents_client_id" not in existing_indexes:
            batch_op.create_index("ix_documents_client_id", ["client_id"])
        if "ix_documents_verification_code" not in existing_indexes:
            batch_op.create_index("ix_documents_verification_code", ["verification_code"], unique=True)

        existing_fks = {fk["name"] for fk in inspector.get_foreign_keys("documents")}
        if "fk_documents_policy_id" not in existing_fks:
            batch_op.create_foreign_key("fk_documents_policy_id", "policies", ["policy_id"], ["id"], ondelete="CASCADE")
        if "fk_documents_client_id" not in existing_fks:
            batch_op.create_foreign_key("fk_documents_client_id", "clients", ["client_id"], ["id"], ondelete="CASCADE")
        if "fk_documents_template_id" not in existing_fks:
            batch_op.create_foreign_key("fk_documents_template_id", "document_templates", ["template_id"], ["id"], ondelete="SET NULL")


def downgrade():
    with op.batch_alter_table("documents") as batch_op:
        batch_op.drop_constraint("fk_documents_template_id", type_="foreignkey")
        batch_op.drop_constraint("fk_documents_client_id", type_="foreignkey")
        batch_op.drop_constraint("fk_documents_policy_id", type_="foreignkey")
        batch_op.drop_index("ix_documents_verification_code")
        batch_op.drop_index("ix_documents_client_id")
        batch_op.drop_index("ix_documents_policy_id")
        batch_op.drop_column("qr_payload")
        batch_op.drop_column("verification_code")
        batch_op.drop_column("template_id")
        batch_op.drop_column("client_id")
        batch_op.drop_column("policy_id")

    op.drop_index("ix_document_templates_code", table_name="document_templates")
    op.drop_table("document_templates")
