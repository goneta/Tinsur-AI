from sqlalchemy import create_engine, text
from app.core.config import settings

def reset_database():
    print(f"Connecting to {settings.DATABASE_URL}...")
    engine = create_engine(settings.DATABASE_URL)
    
    print("Dropping schema public cascade...")
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))
        conn.commit()
    print("Schema reset.")

if __name__ == "__main__":
    reset_database()
