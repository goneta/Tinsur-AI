import sys
import os
from sqlalchemy import text

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine
from app.models.client import Client
from app.models.premium_policy import PremiumPolicyType

def check():
    print(f"Engine URL: {engine.url}")
    
    db = SessionLocal()
    try:
        # Check Clients
        clients = db.query(Client).all()
        print(f"Total Clients in App DB: {len(clients)}")
        for c in clients:
            print(f" - {c.email} ({c.first_name} {c.last_name})")
            
        # Check Policies
        policies = db.query(PremiumPolicyType).all()
        print(f"Total Policies in App DB: {len(policies)}")
        for p in policies:
            print(f" - {p.name} (Company ID: {p.company_id})")

        # Check Admin
        from app.models.user import User
        admin = db.query(User).filter(User.email == "admin@demoinsurance.com").first()
        if admin:
            print(f"Admin Found: {admin.email}, Company ID: {admin.company_id}")
        else:
            print("Admin User NOT found!")
            
        if clients and admin:
             match = clients[0].company_id == admin.company_id
             print(f"Client/Admin Company Match: {match}")

            
    except Exception as e:
        print(f"Error querying DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check()
