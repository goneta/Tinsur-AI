from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./insurance.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def reset_password():
    db = SessionLocal()
    try:
        email = "admin@demoinsurance.com"
        new_password = "Password123!"
        hashed_pw = pwd_context.hash(new_password)
        
        # Check if user exists
        result = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email})
        user = result.fetchone()
        
        if user:
            print(f"Updating password for {email} (ID: {user[0]})...")
            db.execute(
                text("UPDATE users SET hashed_password = :hp WHERE id = :id"), 
                {"hp": hashed_pw, "id": user[0]}
            )
            db.commit()
            print("Password updated successfully.")
        else:
             print("Admin user not found!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_password()
