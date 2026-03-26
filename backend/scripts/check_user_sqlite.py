import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import create_engine, text
from app.core.config import settings

def check_user():
    print(f"Checking DB: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    try:
        with engine.connect() as conn:
            # Check table existence
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users';"))
            if not result.fetchone():
                print("Table 'users' DOES NOT EXIST!")
                return

            # Check user
            result = conn.execute(text("SELECT id, email, hashed_password FROM users WHERE email='admin@demoinsurance.com';"))
            user = result.fetchone()
            if user:
                print(f"User FOUND: {user.email}")
            else:
                print("User admin@demoinsurance.com NOT FOUND!")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_user()
