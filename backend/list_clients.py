
import sys
import os

# Ensure app can be imported
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.client import Client
from app.models.company import Company

def list_clients():
    db = SessionLocal()
    try:
        clients = db.query(Client).all()
        print(f"\n--- Total Clients: {len(clients)} ---")
        if not clients:
            print("No clients found in the database.")
        
        for c in clients:
            company_name = "Unknown"
            if c.company_id:
                comp = db.query(Company).filter(Company.id == c.company_id).first()
                if comp:
                    company_name = comp.name
            
            print(f"ID: {c.id}")
            print(f"Name: {c.first_name} {c.last_name}")
            print(f"Email: {c.email}")
            print(f"Company ID: {c.company_id} ({company_name})")
            print(f"Status: {c.status}")
            print("-" * 30)
            
    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_clients()
