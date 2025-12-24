"""
List all tables in the database (improved).
"""
from sqlalchemy import create_engine, inspect
from app.core.config import settings

def list_tables():
    print(f"Connecting to {settings.DATABASE_URL}...")
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Total tables: {len(tables)}")
    for t in sorted(tables):
        print(f"- {t}")

if __name__ == "__main__":
    list_tables()
