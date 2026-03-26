
import sys
import os
# Ensure backend module is in path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check existing columns using PRAGMA (SQLite specific)
        # If using Postgres, this needs to be queries against information_schema
        # But for now assuming SQLite based on previous scripts
        try:
            result = conn.execute(text("PRAGMA table_info(client_drivers)")).fetchall()
            existing_columns = [row[1] for row in result]
            print(f"Existing columns: {existing_columns}")
            
            columns_to_add = [
                ("license_type", "TEXT"),
                ("cars_in_household", "INTEGER DEFAULT 0"),
                ("residential_status", "TEXT"),
                ("accident_count", "INTEGER DEFAULT 0"),
                ("no_claims_years", "INTEGER DEFAULT 0"),
                ("driving_license_years", "INTEGER DEFAULT 0")
            ]
            
            for col_name, col_type in columns_to_add:
                if col_name not in existing_columns:
                    print(f"Adding column '{col_name}'...")
                    try:
                        conn.execute(text(f"ALTER TABLE client_drivers ADD COLUMN {col_name} {col_type}"))
                        print(f"Added '{col_name}' successfully.")
                    except Exception as e:
                        print(f"Error adding '{col_name}': {e}")
                else:
                    print(f"Column '{col_name}' already exists.")
            
            conn.commit()
            print("Migration Check Complete.")
            
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
