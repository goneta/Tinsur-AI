import sys
import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

DATABASE_URL = os.getenv("DATABASE_URL")

def list_tables():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    print("Tables found:")
    for table_name in inspector.get_table_names():
        print(f" - {table_name}")
        for column in inspector.get_columns(table_name):
            print(f"   * {column['name']} ({column['type']})")

if __name__ == "__main__":
    list_tables()
