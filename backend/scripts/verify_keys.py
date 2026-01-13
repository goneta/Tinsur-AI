
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.translation import Translation

def verify_keys():
    db = SessionLocal()
    keys_to_check = [
        "Total Clients",
        "Active Policies",
        "Pending Quotes",
        "Dashboard Overview",
        "Policy summary",
        "View documents",
        "Payment"
    ]
    
    print("Verifying translation keys in database...")
    for key in keys_to_check:
        exists_en = db.query(Translation).filter(Translation.key == key, Translation.language_code == 'en').first()
        exists_fr = db.query(Translation).filter(Translation.key == key, Translation.language_code == 'fr').first()
        
        print(f"Key: '{key}'")
        print(f"  - EN: {'FOUND' if exists_en else 'MISSING'}")
        print(f"  - FR: {'FOUND' if exists_fr else 'MISSING'}")
        if exists_fr:
            print(f"    -> Value: {exists_fr.value}")
            
    db.close()

if __name__ == "__main__":
    verify_keys()
