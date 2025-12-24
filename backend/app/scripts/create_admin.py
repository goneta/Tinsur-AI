"""
Create default admin user: admin@demoinsurance.com
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.models.company import Company
from app.core.security import get_password_hash
import uuid

# Database URL - adjust if needed
DATABASE_URL = "postgresql://postgres:password@localhost:5432/insurance_saas"

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    print("Creating default admin user...")
    
    # Check if user exists
    admin_email = "admin@demoinsurance.com"
    existing_user = db.query(User).filter(User.email == admin_email).first()
    
    if existing_user:
        print(f"User {admin_email} already exists. Updating password...")
        existing_user.password_hash = get_password_hash("Admin123!")
        db.commit()
        print(f"✓ Password updated for {admin_email}")
    else:
        # Ensure company exists
        company = db.query(Company).filter(Company.name == "Demo Insurance Co").first()
        if not company:
            print("Creating default company...")
            company = Company(
                name="Demo Insurance Co",
                domain="demoinsurance.com",
                is_active=True
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            print("✓ Company created")
        
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
        print(f"✓ Admin user created: {admin_email}")
        print(f"  Password: Admin123!")
        print(f"  Role: super_admin")
    
    db.close()
    print("\n✓ Done! You can now login with:")
    print(f"  Email: admin@demoinsurance.com")
    print(f"  Password: Admin123!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
