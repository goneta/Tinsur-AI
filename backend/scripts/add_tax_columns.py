
import sys
import os
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv() 

from sqlalchemy import text
from app.core.database import engine

def migrate():
    with engine.connect() as conn:
        try:
            print("Adding tax_percent column...")
            conn.execute(text("ALTER TABLE quotes ADD COLUMN tax_percent NUMERIC(5, 2) DEFAULT 0"))
            print("Adding tax_amount column...")
            conn.execute(text("ALTER TABLE quotes ADD COLUMN tax_amount NUMERIC(15, 2) DEFAULT 0"))
            conn.commit()
            print("Migration successful.")
        except Exception as e:
            print(f"Migration error (columns might already exist): {e}")

if __name__ == "__main__":
    migrate()
