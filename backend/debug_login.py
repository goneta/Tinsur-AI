from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password

def check_user(email):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User {email} NOT FOUND.")
        else:
            print(f"User Found: {user.email}")
            print(f"ID: {user.id}")
            print(f"Role: {user.role}")
            print(f"Is Active: {user.is_active}")
            print(f"Is Verified: {user.is_verified}")
            print(f"Company ID: {user.company_id}")
            
            # Since I don't know the password the user is trying, I can't verify it,
            # but I can reset it if needed or check if the hash looks valid.
            print(f"Password Hash Present: {'Yes' if user.password_hash else 'No'}")

    except Exception as e:
        print(f"Error checking user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_user("agent@example.com")
