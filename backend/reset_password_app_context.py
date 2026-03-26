import sys
import os

# Ensure app is in path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def reset_admin():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@demoinsurance.com").first()
        if not user:
            print("User admin@demoinsurance.com not found!")
            return
        
        print(f"Found user: {user.email}")
        new_hash = get_password_hash("admin123")
        user.password_hash = new_hash
        user.is_active = True
        db.commit()
        print("Password reset to 'admin123' and user activated.")
        
        # Verify
        print(f"Stored hash prefix: {user.password_hash[:20]}...")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin()
