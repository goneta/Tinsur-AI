
import sys
import os
import logging
import traceback
from uuid import uuid4
from decimal import Decimal

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.quote_service import QuoteService
from app.repositories.quote_repository import QuoteRepository
from app.models.client import Client
from app.models.premium_policy import PremiumPolicyType
from app.models.company import Company
from app.models.user import User

def reproduce():
    db = SessionLocal()
    try:
        print("--- REPRODUCTION START ---")
        
        # 1. Get Prerequisites
        company = db.query(Company).first()
        if not company:
            print("ERROR: No company found")
            return

        client = db.query(Client).first()
        if not client:
            print("ERROR: No client found")
            return

        policy = db.query(PremiumPolicyType).first()
        if not policy:
            print("ERROR: No policy found")
            return
            
        user = db.query(User).first()
        if not user:
            print("ERROR: No user found")
            return

        print(f"Client: {client.id}")
        print(f"Policy: {policy.id}")
        print(f"User: {user.id}")

        # 2. Mock Data
        risk_factors = {
            "driver_age": 25,
            "vehicle_value": 5000000,
            "accidents": 0
        }
        
        overrides = {
            "base_rate": 0.05,
            "risk_multiplier": [1.2, 1.1],
            "government_tax": [18.0]
        }

        # 3. Call Service
        repo = QuoteRepository(db)
        service = QuoteService(repo)
        
        print("Attempting to create quote...")
        try:
            quote = service.create_quote(
                company_id=company.id,
                client_id=client.id,
                policy_type_id=policy.id,
                coverage_amount=Decimal("5000000"),
                risk_factors=risk_factors,
                premium_frequency="annual",
                duration_months=12,
                created_by=user.id,
                financial_overrides=overrides
            )
            print("SUCCESS! Quote created.")
            print(f"Quote ID: {quote.id}")
            print(f"Premium: {quote.final_premium}")
            
        except Exception as e:
            print("\n!!! EXCEPTION CAUGHT !!!")
            print("-" * 60)
            traceback.print_exc()
            print("-" * 60)
            
    finally:
        db.close()

if __name__ == "__main__":
    reproduce()
