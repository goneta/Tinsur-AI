import asyncio
import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.company import Company
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_admin():
    db = SessionLocal()
    try:
        admin_email = "admin@demoinsurance.com"
        user = db.query(User).filter(User.email == admin_email).first()
        
        if user:
            logger.info(f"Admin user {admin_email} already exists.")
            # Optional: Reset password if needed, but for now just verify existence
            return

        logger.info(f"Admin user {admin_email} not found. Creating...")
        
        # Ensure default company exists
        company = db.query(Company).filter(Company.name == "Demo Insurance Co").first()
        if not company:
            company = Company(name="Demo Insurance Co", domain="demoinsurance.com")
            db.add(company)
            db.commit()
            db.refresh(company)
            logger.info("Created default company 'Demo Insurance Co'")
            
        # Create Admin
        admin_user = User(
            email=admin_email,
            password_hash=get_password_hash("admin123"),
            first_name="Admin",
            last_name="User",
            role="super_admin",
            company_id=company.id,
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)
        db.commit()
        logger.info(f"Successfully created admin user: {admin_email} / admin123")
        
    except Exception as e:
        logger.error(f"Error verifying admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_admin()
