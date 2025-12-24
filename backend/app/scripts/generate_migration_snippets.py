import sys
import os
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.database import Base, engine
import app.models # Ensure all models are loaded

def generate_snippets():
    # Phase 7 tables we want to generate snippets for
    target_tables = [
        'inter_company_shares', 'tickets', 'referrals', 
        'loyalty_points', 'telematics_data', 'ml_models', 'claims'
    ]
    
    # We'll use a dummy context to help generate Alembic-like output if possible, 
    # but direct DDL is easier to adapt.
    
    print("--- Alembic Migration Snippets (Manual Adaptation Required) ---\n")
    
    # Map of table name to its metadata
    table_map = {table.name: table for table in Base.metadata.sorted_tables}
    
    for table_name in target_tables:
        if table_name in table_map:
            table = table_map[table_name]
            print(f"# Table: {table_name}")
            # This prints the SQL, but we want the op.create_table syntax.
            # I'll try to generate a readable summary.
            
            cols = []
            for col in table.columns:
                col_name = col.name
                col_type = str(col.type.compile(postgresql.dialect()))
                nullable = col.nullable
                default = col.default
                pk = col.primary_key
                fk = [str(f.target_fullname) for f in col.foreign_keys]
                
                col_str = f"sa.Column('{col_name}', sa.{col.type.__class__.__name__}(), "
                if pk: col_str += "primary_key=True, "
                if not nullable: col_str += "nullable=False, "
                if fk: col_str += f"sa.ForeignKey('{fk[0]}'), "
                col_str += ")"
                cols.append(col_str)
            
            print(f"op.create_table('{table_name}',")
            for c in cols:
                print(f"    {c},")
            print(")\n")
        else:
            print(f"# Table: {table_name} NOT FOUND in metadata\n")

if __name__ == "__main__":
    generate_snippets()
