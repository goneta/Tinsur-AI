import sys
import os
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import uuid

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine

# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255))
    domain = Column(String(255))
    is_active = Column(Boolean, default=True)

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"))
    email = Column(String(255))
    password_hash = Column(String(255))
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

def reset_admin_orm():
    print("Connecting via ORM (String IDs)...")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        admin_email = "admin@demoinsurance.com"
        print(f"Checking for user: {admin_email}")
        
        user = session.query(User).filter(User.email == admin_email).first()
        
        if user:
            print(f"User found ({user.id}). Updating password...")
            user.password_hash = get_password_hash("admin123")
            session.commit()
            print("✓ Password updated.")
        else:
            print("User not found. Creating...")
            # Check company
            company = session.query(Company).filter(Company.name == "Demo Insurance Co").first()
            if not company:
                print("Creating company...")
                company = Company(
                    name="Demo Insurance Co",
                    domain="demoinsurance.com",
                    is_active=True
                )
                session.add(company)
                session.commit()
                session.refresh(company)
            
            user = User(
                email=admin_email,
                password_hash=get_password_hash("admin123"),
                first_name="Admin",
                last_name="User",
                role="super_admin",
                company_id=company.id,
                is_active=True,
                is_verified=True
            )
            session.add(user)
            session.commit()
            print(f"✓ User created ({user.id}).")
            
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    reset_admin_orm()
