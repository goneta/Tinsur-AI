
import os
import sys
from sqlalchemy.orm import Session

# Ensure backend root is in path
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_root)

from app.core.database import SessionLocal, engine
from app.models.user import User

def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Found {len(users)} users.")
        for u in users:
            print(f"User: {u.email} - Role: {u.role}")
            if u.email == "admin@demoinsurance.com":
                 print("Admin found.")
                 # we can't check password hash easily but we know user exists
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
