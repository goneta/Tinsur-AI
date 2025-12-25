from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.company import Company
from app.core.security import get_password_hash
import uuid

def create_admin():
    db = SessionLocal()
    try:
        # 1. Ensure Company Exists
        company_name = "Demo Insurance Co"
        domain = "demoinsurance.com"
        
        company = db.query(Company).filter(Company.subdomain == domain).first()
        if not company:
            print(f"Creating company: {company_name}")
            company = Company(
                name=company_name,
                subdomain=domain,
                email=f"contact@{domain}",
                is_active=True,
                currency="XOF",
                country="Côte d'Ivoire"
            )
            db.add(company)
            db.commit()
            db.refresh(company)
        else:
            print(f"Company verified: {company.name}")

        # 2. Ensure Admin User Exists
        email = f"admin@{domain}"
        password = "admin123"
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"Creating admin user: {email}")
            user = User(
                email=email,
                password_hash=get_password_hash(password),
                first_name="Super",
                last_name="Admin",
                role="super_admin",
                company_id=company.id,
                is_active=True,
                is_verified=True
            )
            db.add(user)
        else:
            print(f"Resetting admin user: {email}")
            user.password_hash = get_password_hash(password)
            user.is_active = True
            user.is_verified = True
            user.role = "super_admin" # Ensure correct role
            
        db.commit()
        print("Admin user ready.")
        print(f"Email: {email}")
        print(f"Password: {password}")

    except Exception as e:
        print(f"Error creating admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
