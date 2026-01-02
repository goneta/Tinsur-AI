
import sys
import os
from uuid import uuid4
from decimal import Decimal

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.models.quote import Quote
from app.models.client import Client
from app.models.premium_policy import PremiumPolicyType, premium_policy_service_association
from app.models.policy_service import PolicyService

from app.services.quote_service import QuoteService
from app.repositories.quote_repository import QuoteRepository

def verify_services():
    db = SessionLocal()
    try:
        print("Starting verification...")
        
        # 1. Clean up old test data (optional but good practice)
        # 2. Get or Create a Premium Policy with Services
        policy_type = db.query(PremiumPolicyType).first()
        if not policy_type:
            print("No PremiumPolicyType found. Creating one...")
            policy_type = PremiumPolicyType(
                id=uuid4(),
                company_id=uuid4(), # This will fail fk check if company doesn't exist, we should use existing company
                name="Test Policy",
                price=100000,
                is_active=True
            )
            # Find a valid company?
            # For simplicity, let's just grep an existing one or fail if empty.
            # Actually, `seed_full_quote_wizard` should have created one.
            # Let's try to query first.
            existing = db.query(PremiumPolicyType).first()
            if existing:
                policy_type = existing
            else:
                print("CRITICAL: Run seed_full_quote_wizard.py first.")
                return

        print(f"Using Policy Type: {policy_type.name} (ID: {policy_type.id})")
        
        # Verify it has services
        if not policy_type.services:
            print("Policy Type has no services. Creating dummy service...")
            service = PolicyService(id=uuid4(), name_en="Free Towing", name_fr="Remorquage Gratuit")
            db.add(service)
            db.commit()
            # Link it
            # Reset session or re-query to link?
            # policy_type.services.append(service) # This might require commit
            # Manual insert to association table if simple append fails
            db.execute(premium_policy_service_association.insert().values(
                policy_type_id=policy_type.id,
                service_id=service.id
            ))
            db.commit()
            print("Added 'Free Towing' service.")
            db.refresh(policy_type)
        else:
            print(f"Policy has {len(policy_type.services)} services: {[s.name_en for s in policy_type.services]}")

        # 3. Create a Quote using this Policy
        repo = QuoteRepository(db)
        service = QuoteService(repo)
        
        # Need a client
        client = db.query(Client).first()
        if not client:
            print("CRITICAL: No client found.")
            return

        print(f"Creating quote for client: {client.first_name}")
        
        # Mock Data
        risk_factors = {"driver_age": 30}
        
        # Match eligibility first? `evaluate_premium_policy` returns services.
        # `create_quote` calls `calculate_premium` which calls `evaluate_premium_policy`.
        
        quote = service.create_quote(
            company_id=policy_type.company_id,
            client_id=client.id,
            policy_type_id=policy_type.id,
            coverage_amount=Decimal(1000000),
            risk_factors=risk_factors,
            premium_frequency='annual',
            created_by=None # System creation
        )
        
        print(f"Quote created: {quote.quote_number}")
        print(f"Included Services in DB: {quote.included_services}")
        
        if quote.included_services and len(quote.included_services) > 0:
            print("SUCCESS: Services are populated.")
        else:
            print("FAILURE: Included Services list is empty.")
            
            # Debug: Check calculation directly
            calc = service.calculate_premium(
                risk_factors=risk_factors,
                company_id=policy_type.company_id,
                policy_type_id=policy_type.id,
                 coverage_amount=Decimal(1000000)
            )
            print("Calculation Result 'included_services':", calc.get('included_services'))
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_services()
