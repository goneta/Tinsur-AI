"""
Reset admin password to 'Password123!'
Standalone script.
"""
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, ForeignKey, text
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

try:
    print("Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    admin_email = "admin@demoinsurance.com"
    new_password = "Password123!"
    password_hash = get_password_hash(new_password)
    
    print(f"Updating user {admin_email}...")
    
    # Use direct SQL update to avoid ORM StaleDataError or session issues
    with engine.connect() as connection:
        result = connection.execute(
            text("UPDATE users SET password_hash = :pwd WHERE email = :email"),
            {"pwd": password_hash, "email": admin_email}
        )
        connection.commit()
        print(f"Rows updated: {result.rowcount}")
        
    if result.rowcount > 0:
        print(f"✓ Password successfully reset to '{new_password}'")
    else:
        print(f"✗ User {admin_email} not found or no change needed!")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
