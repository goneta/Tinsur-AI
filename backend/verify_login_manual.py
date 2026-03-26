import sys
import os

# Ensure we can import app modules
sys.path.append(os.getcwd())
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest

def test_login_crash():
    db = SessionLocal()
    email = "admin@demoinsurance.com"
    password = "admin123"
    
    print(f"Testing login for {email} with password '{password}'...")
    
    try:
        # Mimic AuthService logic
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print("User not found!")
            return

        print(f"User found. Hash: {user.password_hash}")
        
        # Test verify_password directly as this is the likely crash point for 500
        print("Attempting verify_password...")
        is_valid = verify_password(password, user.password_hash)
        print(f"Password valid? {is_valid}")
        
        if is_valid:
            print("Login logic OK (at least up to password verification).")
            
            # Now test token creation
            print("Attempting to create tokens...")
            from app.core.security import create_access_token
            from app.core.config import settings
            print(f"Using Secret Key: {settings.SECRET_KEY[:5]}... Algorithm: {settings.ALGORITHM}")
            
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
                "company_id": str(user.company_id)
            }
            token = create_access_token(token_data)
            print(f"Token created successfully: {token[:10]}...")
            
        else:
            print("Password invalid.")

    except Exception as e:
        print("CRASH DETECTED!")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_login_crash()
