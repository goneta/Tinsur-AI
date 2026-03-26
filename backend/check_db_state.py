from sqlalchemy import create_engine, inspect
from app.core.config import settings

def check_tables():
    database_url = settings.DATABASE_URL
    engine = create_engine(database_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    has_settings = 'settings' in tables
    
    cols = [c['name'] for c in inspector.get_columns('companies')]
    has_reg = 'registration_number' in cols
    
    print(f"HAS_SETTINGS={has_settings}")
    print(f"HAS_REGISTRATION={has_reg}")

if __name__ == "__main__":
    check_tables()
