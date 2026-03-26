
import sys
import os

# Add parent dir to path (backend)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.client import Client
from app.models.company import Company

def debug_clients():
    db = SessionLocal()
    try:
        print("--- Debugging Client Visibility ---")
        
        # 1. Get Admin User
        admin_email = "admin@demoinsurance.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            print(f"❌ Admin user {admin_email} NOT FOUND!")
            return
            
        print(f"✅ Admin found: {admin.first_name} {admin.last_name}")
        print(f"   Admin Company ID: {admin.company_id}")
        
        company = db.query(Company).filter(Company.id == admin.company_id).first()
        if not company:
             print("❌ Admin Company NOT FOUND!")
        else:
             print(f"   Company Name: {company.name}")
        
        # 2. Get All Clients
        clients = db.query(Client).all()
        print(f"\nFound {len(clients)} total clients in DB.")
        
        print("\n--- Client List ---")
        for c in clients:
            match = "✅ MATCH" if str(c.company_id) == str(admin.company_id) else "❌ MISMATCH"
            print(f"Client: {c.first_name} {c.last_name} ({c.email})")
            print(f"   Company ID: {c.company_id} [{match}]")
            print(f"   Status: {c.status}")
        
    finally:
        db.close()

if __name__ == "__main__":
    debug_clients()
