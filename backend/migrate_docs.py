
from sqlalchemy import create_engine, text
import os
import sys

# Add parent dir to path to find app config if needed, 
# but here we just need the DB URL.
# Assuming standard dev URL or fetching from env.
DATABASE_URL = "postgresql://postgres:postgres@localhost/insurance_saas"

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Migrating documents table...")
        
        # Add scope
        try:
            conn.execute(text("ALTER TABLE documents ADD COLUMN scope VARCHAR(20) DEFAULT 'B2B'"))
            print("Added scope column.")
        except Exception as e:
            print(f"Scope column might exist: {e}")
            
        # Add is_shareable
        try:
            conn.execute(text("ALTER TABLE documents ADD COLUMN is_shareable BOOLEAN DEFAULT FALSE"))
            print("Added is_shareable column.")
        except Exception as e:
            print(f"is_shareable column might exist: {e}")

        # Add reshare_rule
        try:
            conn.execute(text("ALTER TABLE documents ADD COLUMN reshare_rule VARCHAR(1) DEFAULT 'C'"))
            print("Added reshare_rule column.")
        except Exception as e:
            print(f"reshare_rule column might exist: {e}")
            
        conn.commit()
        print("Migration complete.")

if __name__ == "__main__":
    migrate()
