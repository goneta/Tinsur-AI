"""
Test client model mapping.
"""
from app.core.database import SessionLocal
from app.models.client import Client
from app.models.company import Company
from app.models.user import User # Import User for Company relationship resolution

def test_client():
    db = SessionLocal()
    try:
        print("Querying clients...")
        count = db.query(Client).count()
        print(f"Clients count: {count}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_client()
