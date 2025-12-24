import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def reset_password(email, new_password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.password_hash = get_password_hash(new_password)
            db.commit()
            print(f"SUCCESS: Password for {email} reset to {new_password}")
        else:
            print(f"ERROR: User {email} not found")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_password("cadmin@demoinsurance.com", "Admin123!")
    # Also ensure admin@demoinsurance.com has it too
    reset_password("admin@demoinsurance.com", "Admin123!")
