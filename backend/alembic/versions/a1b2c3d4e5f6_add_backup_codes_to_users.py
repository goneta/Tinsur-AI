"""add backup_codes to users

Revision ID: a1b2c3d4e5f6
Revises: ff1f8ba28384
Create Date: 2026-04-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'a1b2c3d4e5f6'
down_revision = '030f8950ddff'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = [c['name'] for c in inspector.get_columns('users')]
    if 'backup_codes' not in cols:
        op.add_column('users', sa.Column('backup_codes', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('users', 'backup_codes')
