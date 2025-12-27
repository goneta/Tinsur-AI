import sys
import os
sys.path.append(os.getcwd())
try:
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.models.policy import Policy
    from app.models.claim import Claim
    from app.models.client import Client
except Exception as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def verify():
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        policy_count = db.query(Policy).count()
        claim_count = db.query(Claim).count()
        client_count = db.query(Client).count()
        
        print(f"Users: {user_count}")
        print(f"Policies: {policy_count}")
        print(f"Claims: {claim_count}")
        print(f"Clients: {client_count}")
        
        admin = db.query(User).filter(User.email == "admin@demoinsurance.com").first()
        if admin:
            print(f"Admin found: {admin.email}, Role: {admin.role}")
        else:
            print("Admin NOT found!")
            
    finally:
        db.close()

if __name__ == "__main__":
    verify()
