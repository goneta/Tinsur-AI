"""refactor_client_company_to_many_to_many

Revision ID: 05a65abc8d6d
Revises: 41024cc3049e
Create Date: 2026-01-19 08:32:17.713151+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '05a65abc8d6d'
down_revision = '41024cc3049e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Rename junction table
    op.rename_table('client_companies', 'client_company')
    
    # 2. Drop company_id from clients
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.drop_column('company_id')

    # 3. Check and drop client_id from users if it exists
    connection = op.get_bind()
    columns = [c['name'] for c in sa.inspect(connection).get_columns('users')]
    if 'client_id' in columns:
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.drop_column('client_id')


def downgrade() -> None:
    # 1. Rename junction table back
    op.rename_table('client_company', 'client_companies')
    
    # 2. Add company_id back to clients
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.add_column(sa.Column('company_id', sa.UUID(), nullable=True))
    
    # Note: client_id in users is not added back as it was likely a mistake or legacy
