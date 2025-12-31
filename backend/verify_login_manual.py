
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password, get_password_hash

def check_login():
    db = SessionLocal()
    try:
        email = "admin@demoinsurance.com"
        password = "admin123"
        
        print(f"Checking user: {email}")
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print("❌ User NOT found in database!")
            return
            
        print(f"User found. ID: {user.id}")
        print(f"Stored Hash: {user.password_hash}")
        
        is_valid = verify_password(password, user.password_hash)
        
        if is_valid:
            print("✅ Password 'admin123' is VALID.")
        else:
            print("❌ Password query FAILED.")
            # Debug: Try hashing it new
            new_hash = get_password_hash(password)
            print(f"New Hash of '{password}': {new_hash}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_login()
