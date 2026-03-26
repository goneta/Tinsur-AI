from sqlalchemy import create_engine, text
from app.core.config import settings

def drop_settings():
    database_url = settings.DATABASE_URL
    engine = create_engine(database_url)
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS settings CASCADE"))
        conn.commit()
    print("Dropped settings table.")

if __name__ == "__main__":
    drop_settings()
