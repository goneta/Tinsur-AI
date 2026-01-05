import requests
import json
import uuid
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./insurance.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

BASE_URL = "http://127.0.0.1:8000/api/v1"
EMAIL = "admin@demoinsurance.com"
PASSWORD = "admin" # Previously failed? Try "admin123" or "Password123!"

def login(email, password):
    print(f"Logging in as {email}...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code != 200:
             print(f"Login failed: {response.text}")
             # Try fallback password?
             if password == "admin":
                 return login(email, "Password123!")
             if password == "Password123!":
                 return login(email, "admin123")
             return None
             
        data = response.json()
        print("Login successful.")
        return data["access_token"]
    except Exception as e:
        print(f"Login exception: {e}")
        return None

def check_db(token):
    # Decode token simply (without verify for speed in script, or rely on requests)
    # Actually, let's just use the DB to find the user by email first
    db = SessionLocal()
    try:
        print(f"Checking DB for user {EMAIL}...")
        result = db.execute(text("SELECT id, email, role, is_active FROM users WHERE email = :email"), {"email": EMAIL})
        user = result.fetchone()
        
        if user:
            print(f"Found User in DB:")
            print(f"  ID: {user[0]}")
            print(f"  Email: {user[1]}")
            print(f"  Role: {user[2]}")
            print(f"  Active: {user[3]}")
            
            # Now verify if THIS ID matches what's in the token?
            # We can't easily decode JWT here without 'jose' library installed in environment?
            # 'jose' is in backend requirements, so it should be there.
            try:
                from jose import jwt
                # Need SECRET_KEY? 
                # Inspecting .env usually helps but we can't.
                # Just print we found the user.
                pass
            except ImportError:
                print("python-jose not installed available in script context?")
                
        else:
            print("!!! User NOT found in DB !!!")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_db(None)
    token = login(EMAIL, "admin123") # Try exact password from seed script output "admin123." (maybe trailing dot is typo in log? "admin123" is likely)
    if token:
        # Decode and check
        from jose import jwt
        # We process without secret just to read claims (dangerous in prod, fine for debug script)
        claims = jwt.get_unverified_claims(token)
        print(f"Token Claims: {claims}")
        
        # Check match
        db_id = "56719f01-e638-486c-8199-73bb240c7e24" # Copy from previous output or fetch again?
        token_id = claims.get("sub")
        print(f"Token ID: {token_id}")
        
        if token_id:
             # Re-check via DB query to be sure
             db = SessionLocal()
             result = db.execute(text("SELECT id FROM users WHERE id = :id"), {"id": token_id})
             match = result.fetchone()
             if match:
                 print("SUCCESS: Token ID matches a Driver in DB.")
             else:
                 print("CRITICAL: Token ID NOT found in DB. Passwords/Seeds out of sync?")
             db.close()
