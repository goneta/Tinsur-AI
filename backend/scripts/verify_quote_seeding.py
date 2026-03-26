
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.client import Client
from app.models.premium_policy import PremiumPolicyType, PremiumPolicyCriteria
from app.models.quote_element import QuoteElement

def verify():
    db = SessionLocal()
    try:
        print("--- VERIFICATION ---")
        clients = db.query(Client).all()
        print(f"Clients: {len(clients)}")
        for c in clients:
            print(f" - {c.first_name} {c.last_name} ({c.email})")

        policies = db.query(PremiumPolicyType).all()
        print(f"\nPremium Policies: {len(policies)}")
        for p in policies:
            print(f" - {p.name} (Price: {p.price}) [Criteria: {len(p.criteria)}]")

        elements = db.query(QuoteElement).all()
        print(f"\nQuote Elements: {len(elements)}")
        by_cat = {}
        for e in elements:
            by_cat.setdefault(e.category, []).append(e)
        
        for cat, items in by_cat.items():
            print(f" Category: {cat}")
            for item in items:
                print(f"   - {item.name}: {item.value}")

    finally:
        db.close()

if __name__ == "__main__":
    verify()
