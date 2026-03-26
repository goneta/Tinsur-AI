import sys
import os
from sqlalchemy import create_engine, text
from passlib.context import CryptContext
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/insurance_saas")

# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def force_reset_admin():
    print("Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Explicitly setting password for admin@demoinsurance.com to 'admin123'...")
        
        new_hash = get_password_hash("admin123")
        
        # Check if user exists
        result = conn.execute(text("SELECT id FROM users WHERE email = 'admin@demoinsurance.com'")).fetchone()
        
        if result:
            conn.execute(
                text("UPDATE users SET password_hash = :pwd WHERE email = :email"),
                {"pwd": new_hash, "email": "admin@demoinsurance.com"}
            )
            print("✓ SUCCESS: Password updated.")
        else:
            print("FAILURE: User not found. Cannot update.")
        
        conn.commit()

if __name__ == "__main__":
    force_reset_admin()
