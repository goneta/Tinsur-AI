
import sys
import os
from sqlalchemy.orm import Session
# Add parent dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def verify_and_reset_admin():
    db = SessionLocal()
    try:
        print("Checking for admin user...")
        email = "admin@demoinsurance.com"
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            print(f"User {email} found. ID: {user.id}")
            print(f"Current Role: {user.role}")
            print(f"Is Active: {user.is_active}")
            
            # Reset password just in case
            new_hash = get_password_hash("admin123")
            user.password_hash = new_hash
            user.is_active = True
            db.commit()
            print("Password reset to 'admin123' and account activated.")
        else:
            print(f"User {email} NOT found!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_and_reset_admin()
