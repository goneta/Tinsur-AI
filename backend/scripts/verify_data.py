
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.company import Company
from app.models.user import User
from app.models.client import Client
from app.models.quote import Quote
from app.models.premium_policy import PremiumPolicyType

def verify():
    db = SessionLocal()
    try:
        print("--- Data Verification ---")
        companies = db.query(Company).all()
        print(f"Companies: {len(companies)}")
        for c in companies:
            print(f" - {c.name} ({c.email})")

        users = db.query(User).all()
        print(f"Users: {len(users)}")
        
        clients = db.query(Client).all()
        print(f"Clients: {len(clients)}")

        policies = db.query(PremiumPolicyType).all()
        print(f"Premium Policies: {len(policies)}")

        quotes = db.query(Quote).all()
        print(f"Quotes: {len(quotes)}")
        for q in quotes:
            print(f" - {q.quote_number} (Status: {q.status})")

    finally:
        db.close()

if __name__ == "__main__":
    verify()
