from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def reset_user(email, new_password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User {email} not found.")
            return

        print(f"Resetting password for {user.email}...")
        user.password_hash = get_password_hash(new_password)
        user.is_active = True
        user.is_verified = True
        
        db.commit()
        print(f"Success! Password set to '{new_password}'. Verified=True, Active=True.")
        
    except Exception as e:
        print(f"Error resetting user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_user("agent@example.com", "password123")
