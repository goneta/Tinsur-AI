import sys
import os
import uuid
from typing import Generator
from sqlalchemy.orm import Session

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.policy import Policy
from app.models.user import User
from app.models.company import Company
from app.core.database import get_db
from app.core.dependencies import get_current_user

def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Mock user for authentication
def override_get_current_user():
    db = SessionLocal()
    try:
        # Get the first admin user found
        user = db.query(User).filter(User.role == "admin").first()
        if not user:
             # Create a dummy one if needed (should exist from robust script)
             pass
        return user
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

def test_api_generation():
    db = SessionLocal()
    try:
        print("Testing API Endpoint...")
        
        # Get a policy
        policy = db.query(Policy).first()
        if not policy:
            print("No policy found.")
            return

        print(f"Using Policy ID: {policy.id}")
        
        # Call Endpoint
        response = client.post(f"/api/v1/policies/{policy.id}/generate-schedule")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 404:
            print("ERROR: Endpoint returned 404.")
        elif response.status_code == 201:
            print("SUCCESS: Endpoint returned 201.")
            
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_api_generation()
