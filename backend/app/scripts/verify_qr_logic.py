
import sys
import os
import uuid
import hmac
import hashlib

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal
from app.models.policy import Policy
from app.core.config import settings

def test_qr_logic():
    print("Testing QR Verification Logic...")
    db = SessionLocal()
    try:
        # Get a policy
        policy = db.query(Policy).first()
        if not policy:
            print("No policies found to test.")
            return

        print(f"Testing with Policy: {policy.policy_number}")
        
        # 1. Generate token
        SECRET_KEY = settings.SECRET_KEY
        token = hmac.new(
            SECRET_KEY.encode(),
            str(policy.id).encode(),
            hashlib.sha256
        ).hexdigest()
        
        print(f"Generated Token: {token[:10]}...")
        
        # 2. Save token
        policy.qr_code_data = token
        db.commit()
        print("Token saved to database.")
        
        # 3. Verify retrieval
        retrieved = db.query(Policy).filter(Policy.qr_code_data == token).first()
        if retrieved and retrieved.id == policy.id:
            print("SUCCESS: Policy retrieved by token.")
        else:
            print("FAILURE: Policy NOT retrieved by token.")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_qr_logic()
