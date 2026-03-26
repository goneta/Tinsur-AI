import sys
import os
import time
import requests
from uuid import uuid4

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.company import Company
from app.core.security import get_password_hash

BASE_URL = "http://localhost:8000/api/v1"

def debug_auth_speed():
    db = SessionLocal()
    try:
        # 1. Setup Test User
        email = f"speedtest_{uuid4()}@example.com"
        password = "password123"
        print(f"Creating test user: {email}")
        
        # Get a company
        company = db.query(Company).first()
        if not company:
            print("ERROR: No company found. Cannot create user.")
            return

        user = User(
            email=email,
            password_hash=get_password_hash(password),
            role="agent",
            company_id=company.id,
            first_name="Speed",
            last_name="Test",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.close() # Close session to release locks
        
        # 2. Login
        print("Logging in...")
        start = time.time()
        resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
        
        data = resp.json()
        token = data["access_token"]
        print(f"Login took: {time.time() - start:.4f}s")
        
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Benchmark /auth/me
        print("Benchmarking /auth/me ...")
        start = time.time()
        resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        duration = time.time() - start
        
        print(f"/auth/me took: {duration:.4f}s")
        if resp.status_code == 200:
            user_data = resp.json()
            # Access checking
            print(f"Got User: {user_data.get('email')}")
        else:
            print(f"Error: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
    finally:
        # Cleanup
        db_clean = SessionLocal()
        try:
             user = db_clean.query(User).filter(User.email == email).first()
             if user:
                 db_clean.delete(user)
                 db_clean.commit()
        except:
             pass
        finally:
             db_clean.close()

if __name__ == "__main__":
    debug_auth_speed()
