from app.core.database import SessionLocal
from app.models.user import User
from app.models.client import Client
from app.core.security import get_password_hash
import uuid

def find_or_create_test_user():
    db = SessionLocal()
    try:
        # Check for Test User
        user = db.query(User).filter(User.email == "test@example.com").first()
        if not user:
            print("Test User not found. Creating...")
            # We need a company
            from app.models.company import Company
            company = db.query(Company).first()
            if not company:
                print("No company found. Cannot create user.")
                return
            
            user = User(
                email="test@example.com",
                password_hash=get_password_hash("password123"),
                first_name="Test",
                last_name="User",
                role="client",
                company_id=company.id,
                is_active=True,
                is_verified=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created Test User: {user.email}")
            
            # Create client profile if missing
            client = db.query(Client).filter(Client.user_id == user.id).first()
            if not client:
                client = Client(
                    user_id=user.id,
                    company_id=company.id,
                    client_type="individual",
                    first_name="Test",
                    last_name="User",
                    email="test@example.com",
                    status="active"
                )
                db.add(client)
                db.commit()
                print("Created Client Profile for Test User.")
        else:
            print(f"Test User found: {user.email}")
            # Ensure it has a client record
            client = db.query(Client).filter(Client.user_id == user.id).first()
            if not client:
                print("Client Profile missing for Test User. Creating...")
                client = Client(
                    user_id=user.id,
                    company_id=user.company_id,
                    client_type="individual",
                    first_name="Test",
                    last_name="User",
                    email="test@example.com",
                    status="active"
                )
                db.add(client)
                db.commit()
                print("Created Client Profile for Test User.")
            else:
                print("Client Profile already exists.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    find_or_create_test_user()
