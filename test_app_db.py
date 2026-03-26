import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal
from app.models.client import Client

def test_db():
    print("Testing app database connection...")
    try:
        db = SessionLocal()
        count = db.query(Client).count()
        print(f"Success! Found {count} clients via app engine.")
        
        clients = db.query(Client).limit(5).all()
        for c in clients:
            print(f"- {c.first_name} {c.last_name} ({c.company_id})")
            
        db.close()
    except Exception as e:
        print(f"Error connecting via app engine: {e}")

if __name__ == "__main__":
    test_db()
