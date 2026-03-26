import sys
import os
from sqlalchemy import create_engine, text

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.config import settings

def check_db():
    print(f"Configured DATABASE_URL: {settings.DATABASE_URL}")
    
    # 1. Access Main DB
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print("\n--- Connecting to Configured DB ---")
        result = conn.execute(text("SELECT email, password_hash, is_active FROM users WHERE email='admin@demoinsurance.com'"))
        row = result.fetchone()
        if row:
            print(f"Found Admin: {row[0]}")
            print(f"Hash: {row[1]}")
            print(f"Active: {row[2]}")
        else:
            print("Admin NOT found in configured DB.")

    # 2. Check fallback/other DB if exists
    if os.path.exists("tinsur.db"):
        print("\n--- Checking 'tinsur.db' (potential split brain) ---")
        engine2 = create_engine("sqlite:///./tinsur.db")
        with engine2.connect() as conn:
             try:
                result = conn.execute(text("SELECT email, password_hash FROM users WHERE email='admin@demoinsurance.com'"))
                row = result.fetchone()
                if row:
                    print(f"Found Admin in tinsur.db: {row[0]}")
                    print(f"Hash: {row[1]}")
                else:
                    print("Admin NOT found in tinsur.db")
             except Exception as e:
                 print(f"Error reading tinsur.db: {e}")

if __name__ == "__main__":
    check_db()
