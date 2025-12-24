import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.company import Company
from app.core.security import get_password_hash

def create_admin():
    db = SessionLocal()
    try:
        # Check if admin exists
        admin_email = "admin@demoinsurance.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        
        if admin:
            print(f"Admin user already exists: {admin_email}")
            print(f"Updating password to 'Admin123!'...")
            admin.password_hash = get_password_hash("Admin123!")
            db.commit()
            print("✓ Password updated successfully!")
        else:
            print(f"Creating admin user: {admin_email}")
            
            # Ensure company exists
            company = db.query(Company).filter(Company.name == "Demo Insurance Co").first()
            if not company:
                company = Company(
                    name="Demo Insurance Co",
                    domain="demoinsurance.com",
                    is_active=True
                )
                db.add(company)
                db.commit()
                db.refresh(company)
                print("✓ Created Demo Insurance Co")
            
            # Create admin user
            admin = User(
                email=admin_email,
                password_hash=get_password_hash("Admin123!"),
                first_name="Admin",
                last_name="User",
                role="super_admin",
                company_id=company.id,
                is_active=True,
                is_verified=True
            )
            db.add(admin)
            db.commit()
            print(f"✓ Admin user created successfully!")
        
        print("\n" + "="*50)
        print("Admin Login Credentials:")
        print("="*50)
        print(f"Email: {admin_email}")
        print(f"Password: Admin123!")
        print("="*50)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
