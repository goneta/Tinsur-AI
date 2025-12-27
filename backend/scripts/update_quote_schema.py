import sys
import os
from sqlalchemy import create_engine, text

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def update_schema():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check current columns
        result = conn.execute(text("PRAGMA table_info(quotes)"))
        columns = [row[1] for row in result.fetchall()]
        
        print(f"Current columns in 'quotes': {columns}")
        
        if 'excess' not in columns:
            print("Adding 'excess' column...")
            try:
                conn.execute(text("ALTER TABLE quotes ADD COLUMN excess NUMERIC(15, 2) DEFAULT 0.0"))
                conn.commit()
                print("Added 'excess'.")
            except Exception as e:
                print(f"Error adding excess: {e}")
        else:
            print("'excess' column already exists.")
            
        if 'included_services' not in columns:
            print("Adding 'included_services' column...")
            try:
                # JSON type in SQLite is just TEXT or generic
                conn.execute(text("ALTER TABLE quotes ADD COLUMN included_services JSON DEFAULT '[]'"))
                conn.commit()
                print("Added 'included_services'.")
            except Exception as e:
                print(f"Error adding included_services: {e}")
        else:
            print("'included_services' column already exists.")

if __name__ == "__main__":
    update_schema()
