"""
Create default admin user: admin@demoinsurance.com
Standalone script - no config dependencies
"""
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./insurance.db")

# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Simple models
Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255))
    domain = Column(String(255))
    is_active = Column(Boolean, default=True)

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    email = Column(String(255))
    password_hash = Column(String(255))
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

try:
    print("Connecting to database...")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    print("Creating default admin user...")
    
    # Check if user exists
    admin_email = "admin@demoinsurance.com"
    existing_user = db.query(User).filter(User.email == admin_email).first()
    
    if existing_user:
        print(f"User {admin_email} already exists. Updating password...")
        existing_user.password_hash = get_password_hash("admin123")
        db.commit()
        print(f"✓ Password updated for {admin_email}")
    else:
        # Ensure company exists
        company = db.query(Company).filter(Company.name == "Demo Insurance Co").first()
        if not company:
            print("Creating default company...")
            company = Company(
                id=uuid.uuid4(),
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
            id=uuid.uuid4(),
            email=admin_email,
            password_hash=get_password_hash("admin123"),
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
    
    db.close()
    print("\n" + "="*50)
    print("✓ SUCCESS! Admin user is ready:")
    print("="*50)
    print(f"  Email: admin@demoinsurance.com")
    print(f"  Password: admin123")
    print(f"  Role: super_admin")
    print("="*50)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
