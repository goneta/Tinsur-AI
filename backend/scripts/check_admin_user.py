import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
# Import models to ensure mappers are registered in correct order
from sqlalchemy import text
from app.core.security import verify_password

def check_admin_user():
    db = SessionLocal()
    try:
        # Use raw SQL to bypass ORM mapper issues
        result = db.execute(text("SELECT id, email, password_hash, is_active, company_id FROM users WHERE email = :email"), {"email": "admin@demoinsurance.com"}).fetchone()
        
        if not result:
            print("FAILURE: User 'admin@demoinsurance.com' NOT FOUND in database.")
            return

        print(f"User Found: {result[1]}")
        print(f"ID: {result[0]}")
        print(f"Status: {result[3]}")
        print(f"Company ID: {result[4]}")
        
        # Verify Password
        is_valid = verify_password("admin123", result[2])
        if is_valid:
            print("SUCCESS: Password 'admin123' matches stored hash.")
        else:
            print("FAILURE: Password 'admin123' DOES NOT match stored hash.")

    except Exception as e:
        print(f"Error checking user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin_user()
