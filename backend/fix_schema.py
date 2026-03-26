
from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

def fix_schema():
    with engine.connect() as conn:
        print("Fixing schema constraints...")
        conn.execute(text("COMMIT"))
        
        try:
            # Postgres syntax
            conn.execute(text("ALTER TABLE inter_company_shares ALTER COLUMN to_company_id DROP NOT NULL"))
            print("Dropped NOT NULL constraint from to_company_id.")
        except Exception as e:
            print(f"Failed to alter column: {e}")

if __name__ == "__main__":
    fix_schema()
