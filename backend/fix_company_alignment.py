import sys
import os
from sqlalchemy import text

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.client import Client
from app.models.premium_policy import PremiumPolicyType, PremiumPolicyCriteria
from app.models.quote_element import QuoteElement
from app.models.quote import Quote

def fix_alignment():
    print("Forcing Company ID Alignment...")
    db = SessionLocal()
    try:
        # 1. Get Admin Company ID
        admin = db.query(User).filter(User.email == "admin@demoinsurance.com").first()
        if not admin:
            print("Admin not found!")
            return
        
        cid = admin.company_id
        print(f"Target Company ID (Admin): {cid}")
        
        # 2. Update Clients
        clients = db.query(Client).all()
        for c in clients:
            c.company_id = cid
        print(f"Aligning {len(clients)} Clients...")
        
        # 3. Update Policies
        pols = db.query(PremiumPolicyType).all()
        for p in pols:
            p.company_id = cid
        print(f"Aligning {len(pols)} Policies...")

        # 4. Update Criteria
        # (This is important as match depends on it)
        crits = db.query(PremiumPolicyCriteria).all()
        for c in crits:
            c.company_id = cid
        print(f"Aligning {len(crits)} Criteria...")

        # 5. Quote Elements
        elems = db.query(QuoteElement).all()
        for e in elems:
            e.company_id = cid
        print(f"Aligning {len(elems)} Quote Elements...")

        db.commit()
        print("Success! All data aligned to Admin Company ID.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_alignment()
