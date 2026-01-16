from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password, get_password_hash

db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@demoinsurance.com').first()

if user:
    print(f"User found: {user.email}")
    print(f"Hash in DB starts with: {user.password_hash[:20] if user.password_hash else 'None'}")
    
    password_to_test = "admin123"
    is_valid = verify_password(password_to_test, user.password_hash)
    print(f"Verifying '{password_to_test}': {is_valid}")
    
    if not is_valid:
        print("Resetting password again...")
        new_hash = get_password_hash(password_to_test)
        user.password_hash = new_hash
        db.commit()
        print("Password reset committed.")
        
        # Verify again
        is_valid_new = verify_password(password_to_test, user.password_hash)
        print(f"Verifying after reset: {is_valid_new}")
else:
    print("User not found")
