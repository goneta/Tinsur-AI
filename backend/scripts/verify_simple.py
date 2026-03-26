
import sys
import os
from sqlalchemy import text
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal

def verify_simple():
    db = SessionLocal()
    try:
        print("--- SIMPLE VERIFICATION ---")
        tables = ["clients", "premium_policy_types", "quote_elements", "premium_policy_criteria"]
        for t in tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {t}"))
                count = result.scalar()
                print(f"{t}: {count}")
            except Exception as e:
                print(f"{t}: Error {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    verify_simple()
