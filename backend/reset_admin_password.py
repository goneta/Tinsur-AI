import sys
import os

# Ensure we can import app modules
sys.path.append(os.getcwd())
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def fix_admin_login():
    db = SessionLocal()
    email = "admin@demoinsurance.com"
    new_password = "admin123"
    
    try:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"User {email} NOT FOUND. Creating...")
            # Ideally we would create, but for now just report failure as user implies it should exist
            # Or we can fallback to finding ANY admin.
            print("Cannot fix missing user without more context (like Company ID).")
            return
            
        print(f"Found user: {user.email} (ID: {user.id})")
        print(f"Current Role: {user.role}")
        print(f"Is Active: {user.is_active}")
        
        # Reset Password
        user.password_hash = get_password_hash(new_password)
        user.is_active = True
        user.is_verified = True # Ensure verified
        
        db.commit()
        print(f"SUCCESS: Password reset to '{new_password}' and account activated.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin_login()
