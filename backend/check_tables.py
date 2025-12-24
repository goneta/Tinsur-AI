from sqlalchemy import create_engine, inspect
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from app.core.config import settings

def check_tables():
    print(f"Connecting to: {settings.DATABASE_URL}")
    engine = create_engine(str(settings.DATABASE_URL))
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables found: {len(tables)}")
    if 'co_insurance_shares' in tables:
        print("SUCCESS: co_insurance_shares table exists.")
    else:
        print("FAILURE: co_insurance_shares table DOEST NOT exist.")
        # List similar
        similar = [t for t in tables if 'insurance' in t]
        print(f"Similar tables: {similar}")

if __name__ == "__main__":
    check_tables()
