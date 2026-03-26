import sys
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.company import Company
from app.models.client import Client
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_auth_users():
    db = SessionLocal()
    try:
        # 1. Fix Admin
        admin_email = "admin@demoinsurance.com"
        admin_pass = "Admin123!"
        
        logger.info(f"Checking {admin_email}...")
        admin = db.query(User).filter(User.email == admin_email).first()
        
        if admin:
            logger.info(f"Resetting password for {admin_email}")
            admin.password_hash = get_password_hash(admin_pass)
            admin.is_active = True
            admin.is_verified = True
            db.commit()
        else:
            logger.info(f"Creating {admin_email}")
            # Ensure company
            company = db.query(Company).filter(Company.name == "Demo Insurance Co").first()
            if not company:
                company = Company(name="Demo Insurance Co", subdomain="demoinsurance.com", email="contact@demoinsurance.com")
                db.add(company)
                db.commit()
                db.refresh(company)
            
            admin = User(
                email=admin_email,
                password_hash=get_password_hash(admin_pass),
                first_name="Admin",
                last_name="User",
                role="super_admin",
                company_id=company.id,
                is_active=True,
                is_verified=True
            )
            db.add(admin)
            db.commit()
            
        logger.info(f"✓ Admin fixed: {admin_email} / {admin_pass}")

        # 2. Fix Client
        client_email = "test_client@tinsur.ai"
        client_pass = "Client123!"
        
        logger.info(f"Checking {client_email}...")
        client_user = db.query(User).filter(User.email == client_email).first()
        
        company = db.query(Company).filter(Company.name == "Demo Insurance Co").first()

        if client_user:
            logger.info(f"Resetting password for {client_email}")
            client_user.password_hash = get_password_hash(client_pass)
            client_user.role = "client" # Ensure role is client
            client_user.is_active = True
            client_user.is_verified = True
            db.commit()
            db.refresh(client_user)
        else:
            logger.info(f"Creating {client_email}")
            client_user = User(
                email=client_email,
                password_hash=get_password_hash(client_pass),
                first_name="Test",
                last_name="Client",
                role="client",
                company_id=company.id,
                is_active=True,
                is_verified=True
            )
            db.add(client_user)
            db.commit()
            db.refresh(client_user)

        # Ensure Client Profile
        client_profile = db.query(Client).filter(Client.user_id == client_user.id).first()
        if not client_profile:
            logger.info(f"Creating Client profile for {client_email}")
            client_profile = Client(
                company_id=company.id,
                user_id=client_user.id,
                client_type="individual",
                first_name=client_user.first_name,
                last_name=client_user.last_name,
                email=client_user.email,
                phone="+225 0707070707",
                status="active"
            )
            db.add(client_profile)
            db.commit()
        
        logger.info(f"✓ Client fixed: {client_email} / {client_pass}")
        
    except Exception as e:
        logger.error(f"Error fixing users: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_auth_users()
