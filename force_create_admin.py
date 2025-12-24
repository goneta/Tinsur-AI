import sys
import os

# Add backend to path
# Assuming we run from project root (Tinsur.AI)
# sys.path.insert(0, os.path.abspath('backend'))
# Actually better to insert backend/
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.company import Company
from app.core.security import get_password_hash

def create():
    db = SessionLocal()
    try:
        # Create tables if not exist (just in case)
        # Base.metadata.create_all(bind=engine) 
        # Skip this if it causes errors due to broken models, but we need users table.
        
        email = "admin@demoinsurance.com"
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"User {email} exists. Updating password.")
            user.password_hash = get_password_hash("Admin123!")
            db.commit()
        else:
            print(f"Creating user {email}")
            # Ensure company
            company = db.query(Company).first()
            if not company:
                company = Company(name="Demo Co", domain="demo.com", is_active=True)
                db.add(company)
                db.commit()
                db.refresh(company)
            
            user = User(
                email=email,
                password_hash=get_password_hash("Admin123!"),
                first_name="Admin",
                last_name="Test",
                role="super_admin",
                company_id=company.id,
                is_active=True,
                is_verified=True
            )
            db.add(user)
            db.commit()
            print("User created.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create()
