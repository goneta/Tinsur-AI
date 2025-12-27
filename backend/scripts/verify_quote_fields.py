import sys
import os
import uuid
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.premium_policy import PremiumPolicyType, PremiumPolicyCriteria
from app.models.policy_service import PolicyService
from app.models.company import Company
from app.services.quote_service import QuoteService
from app.repositories.quote_repository import QuoteRepository
from app.models.quote import Quote
from app.models.client import Client
from app.models.policy_type import PolicyType

def verify_fields():
    db = SessionLocal()
    try:
        print("Setting up test data...")
        
        # 1. Create Company
        company = Company(name="Test Company", currency="XOF")
        db.add(company)
        db.commit()
        
        # 2. Create Policy Service
        service = PolicyService(
            company_id=company.id,
            name_en="Test Service 1",
            default_price=1000
        )
        db.add(service)
        db.commit()
        
        # 3. Create Premium Policy Type with excess and services
        premium_policy = PremiumPolicyType(
            company_id=company.id,
            name="Gold Plan",
            price=50000,
            excess=5000,
            is_active=True
        )
        db.add(premium_policy)
        db.commit()
        
        # Add service to policy (access association manually or via relationship?)
        # premium_policy.services.append(service) -> This works if configured
        # But we need to be careful with tables. premium_policy_service_association
        # Let's try appending
        try:
             premium_policy.services.append(service)
             db.commit()
        except Exception as e:
            print(f"Warning: Could not link service: {e}")

        # 4. Create dummy criterion to ensure it matches
        # We need a criterion that matches everything, e.g. age > 0
        crit = PremiumPolicyCriteria(
             company_id=company.id,
             name="All Ages",
             field_name="driver_age",
             operator=">",
             value="0"
        )
        premium_policy.criteria.append(crit)
        db.commit()


        # 5. Create Client
        client = Client(company_id=company.id, first_name="John", last_name="Doe", email="john@example.com")
        db.add(client)
        db.commit()

        # 6. Create PolicyType (Standard)
        pt = PolicyType(company_id=company.id, name="Auto", code="AUTO")
        db.add(pt)
        db.commit()

        # 7. Quote Service Calculation
        repo = QuoteRepository(db)
        service = QuoteService(repo)
        
        risk_factors = {"driver_age": 30, "coverage_amount": 100000}
        
        print("Calculating premium...")
        # We need to simulate the flow where it finds the PremiumPolicy
        # evaluate_premium_policy(company_id, risk_factors)
        
        eval_result = service.evaluate_premium_policy(company.id, risk_factors)
        print(f"Evaluation Result: {eval_result}")
        
        if not eval_result:
            print("ERROR: Premium Policy not matched!")
            return

        print("Creating quote...")
        quote = service.create_quote(
            company_id=company.id,
            client_id=client.id,
            policy_type_id=pt.id,
            coverage_amount=Decimal(100000),
            risk_factors=risk_factors
        )
        
        print(f"Created Quote ID: {quote.id}")
        print(f"Quote Excess: {quote.excess}")
        print(f"Quote Included Services: {quote.included_services}")
        
        if quote.excess == 5000 and "Test Service 1" in quote.included_services:
            print("SUCCESS: Quote has correct excess and services.")
        else:
            print("FAILURE: Quote missing expected data.")
            print(f"Expected excess: 5000, got {quote.excess}")
            print(f"Expected services: ['Test Service 1'], got {quote.included_services}")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_fields()
