import sys
import os
from sqlalchemy import text

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User

def reset_admin_password():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@demoinsurance.com").first()
        if not user:
            print("User not found!")
            return

        new_hash = get_password_hash("password123")
        print(f"Old Hash Start: {user.password_hash[:20]}...")
        
        user.password_hash = new_hash
        db.commit()
        
        print(f"New Hash Start: {new_hash[:20]}...")
        print("Password reset successfully for admin@demoinsurance.com to 'password123'")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()
