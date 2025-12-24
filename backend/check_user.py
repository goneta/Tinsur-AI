from app.core.database import SessionLocal
from app.models import *
from app.models.user import User

def check_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@demoinsurance.com").first()
        if user:
            print(f"User found: {user.email}, Role: {user.role}")
        else:
            print("User not found")
    finally:
        db.close()

if __name__ == "__main__":
    check_user()
