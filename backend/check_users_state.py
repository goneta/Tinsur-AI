from sqlalchemy import create_engine, inspect
from app.core.config import settings

def check_users():
    database_url = settings.DATABASE_URL
    engine = create_engine(database_url)
    inspector = inspect(engine)
    
    cols = inspector.get_columns('users')
    id_col = next((c for c in cols if c['name'] == 'id'), None)
    print(f"ID_COL_TYPE={id_col['type'] if id_col else 'MISSING'}")
    
    pk = inspector.get_pk_constraint('users')
    print(f"PK={pk}")

if __name__ == "__main__":
    check_users()
