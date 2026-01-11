import os
import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
import uuid

def seed():
    db = SessionLocal()
    try:
        email = "test_client@tinsur.ai"
        # Check if already exists
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"User {email} already exists.")
            return

        # Use the Test Client company ID found earlier
        company_id = "f42af750-882c-43fc-bc2d-14073cc4b6f7"
        
        new_user = User(
            id=uuid.uuid4(),
            company_id=uuid.UUID(company_id),
            email=email,
            password_hash=get_password_hash("Password123!"),
            first_name="Test",
            last_name="Client",
            role="client",
            is_active=True,
            is_verified=True
        )
        db.add(new_user)
        db.commit()
        print(f"User {email} seeded successfully.")
    except Exception as e:
        print(f"Error seeding user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Add project root to sys.path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(project_root, "backend"))
    seed()
