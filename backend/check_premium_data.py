from sqlalchemy import text
from app.core.database import SessionLocal
import sys
import os

sys.path.append(os.getcwd())

def check_premium_data():
    db = SessionLocal()
    try:
        print("Checking Premium Policy Types:")
        policies = db.execute(text("SELECT id, name, price FROM premium_policy_types")).all()
        for p in policies:
            print(f"  - {p.name} (Price: {p.price})")
            
        print("\nChecking Policy Services:")
        services = db.execute(text("SELECT id, name_en, default_price FROM policy_services")).all()
        for s in services:
            print(f"  - {s.name_en} (Price: {s.default_price})")
            
        print("\nChecking Association:")
        assoc = db.execute(text("SELECT * FROM premium_policy_service_association")).all()
        print(f"Total associations: {len(assoc)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_premium_data()
