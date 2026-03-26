import requests
import sys
import os

# Add backend to path to import app modules for token generation
sys.path.append(os.getcwd())
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import create_access_token

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "test_client@tinsur.ai"

def verify_http_with_forced_token():
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.email == EMAIL).first()
        if not user:
            print(f"User {EMAIL} not found in DB!")
            return
            
        print(f"Found user {user.id}. Generating token manually...")
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "company_id": str(user.company_id)
        }
        token = create_access_token(token_data)
        print(f"Token generated.")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Test Referral Generation
        print("Attempting to generate referral code...")
        ref_resp = requests.post(f"{BASE_URL}/portal/referrals", headers=headers)
        
        print(f"Referral Response Code: {ref_resp.status_code}")
        print(f"Referral Response Body: {ref_resp.text}")
        
        if ref_resp.status_code == 200:
            data = ref_resp.json()
            print("\nSUCCESS!")
            print(f"Referral Code: {data.get('referral_code')}")
            print(f"Status: {data.get('status')}")
        else:
            print("\nFAILURE!")
            
    except Exception as e:
        print(f"Uncaught Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_http_with_forced_token()
