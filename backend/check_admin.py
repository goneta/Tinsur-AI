import sys
import os

# Ensure we can import app modules
sys.path.append(os.getcwd())
from app.core.database import SessionLocal
from app.models.user import User

def check_admin_details():
    db = SessionLocal()
    email = "admin@demoinsurance.com"
    
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"User: {user.email}")
            print(f"Company ID: {user.company_id}")
            print(f"Type of Company ID: {type(user.company_id)}")
            print(f"Stringified: {str(user.company_id)}")
        else:
            print("User not found")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin_details()
