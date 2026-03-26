
import sys
import os
from decimal import Decimal
import uuid
import asyncio
from datetime import date

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.quote import Quote
from app.models.underwriting import UnderwritingReferral
from app.services.quote_service import QuoteService
from app.services.underwriting_service import UnderwritingService
from app.repositories.quote_repository import QuoteRepository

async def verify_underwriting_referral():
    print("Ensuring Underwriting tables exist...")
    Base.metadata.create_all(bind=engine)
    
    print("Verifying Underwriting Authority & Referral Flow...")
    db = SessionLocal()
    try:
        # 1. Setup Test Users
        # Get an existing user to use for company_id etc.
        base_user = db.query(User).first()
        if not base_user:
            print("No users found for testing.")
            return

        # Create/Update an Agent with $10,000 limit
        agent = db.query(User).filter(User.email == 'agent@test.com').first()
        if not agent:
            agent = User(
                email='agent@test.com',
                password_hash='dummy',
                first_name='Test',
                last_name='Agent',
                role='agent',
                company_id=base_user.company_id,
                underwriting_limit=Decimal("10000.00")
            )
            db.add(agent)
            db.commit()
            print("Test Agent Created with $10,000 limit.")
        else:
            agent.underwriting_limit = Decimal("10000.00")
            db.commit()
            print("Test Agent Limit reset to $10,000.")

        # Create/Update a Manager
        manager = db.query(User).filter(User.email == 'manager@test.com').first()
        if not manager:
            manager = User(
                email='manager@test.com',
                password_hash='dummy',
                first_name='Test',
                last_name='Manager',
                role='manager',
                company_id=base_user.company_id
            )
            db.add(manager)
            db.commit()
            print("Test Manager Created.")

        # 2. Test Referral Trigger (Quote for $50,000 coverage)
        quote_service = QuoteService(QuoteRepository(db))
        
        # We need a policy type and client
        from app.models.policy_type import PolicyType
        from app.models.client import Client
        policy_type = db.query(PolicyType).first()
        if not policy_type:
            policy_type = PolicyType(
                company_id=base_user.company_id,
                name="Test Policy Type",
                code="AUTO",
                description="Test coverage"
            )
            db.add(policy_type)
            db.commit()
            print("Test Policy Type Created.")
            
        client = db.query(Client).filter(Client.company_id == base_user.company_id).first()
        
        if not (policy_type and client):
            print("PolicyType or Client missing for test.")
            return

        print("\nAttempting to create $50,000 quote (Agent limit $10,000)...")
        quote = quote_service.create_quote(
            company_id=base_user.company_id,
            client_id=client.id,
            policy_type_id=policy_type.id,
            coverage_amount=Decimal("50000.00"),
            risk_factors={'driver_age': 30},
            created_by=agent.id
        )
        
        print(f"Quote Created: {quote.quote_number}, Status: {quote.status}")
        
        if quote.status == 'referred':
            print("SUCCESS: Quote correctly flagged as 'referred'.")
        else:
            print(f"FAILURE: Expected status 'referred', got '{quote.status}'")

        # 3. Check for Referral Record
        referral = db.query(UnderwritingReferral).filter(UnderwritingReferral.quote_id == quote.id).first()
        if referral:
            print(f"SUCCESS: Referral Record found. Reason: {referral.reason}")
        else:
            print("FAILURE: No referral record created.")

        # 4. Test Manager Approval
        print("\nProcessing Manager Approval...")
        underwriting_service = UnderwritingService(db)
        underwriting_service.process_referral_decision(
            referral_id=referral.id,
            decided_by_id=manager.id,
            status='approved',
            notes="Risk is acceptable despite high value."
        )
        
        db.refresh(quote)
        db.refresh(referral)
        print(f"Referral Status: {referral.status}")
        print(f"Quote Status: {quote.status}")
        
        if quote.status == 'accepted':
            print("SUCCESS: Quote correctly marked as 'accepted' after approval.")
        else:
            print(f"FAILURE: Quote status should be 'accepted', got '{quote.status}'")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(verify_underwriting_referral())
