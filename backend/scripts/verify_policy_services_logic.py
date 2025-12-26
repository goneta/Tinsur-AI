import sys
import os
from datetime import date, timedelta
from decimal import Decimal
import uuid

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.company import Company
from app.models.user import User
from app.models.client import Client
from app.models.policy_type import PolicyType
from app.models.policy_service import PolicyService as PolicyServiceModel, policy_service_association
from app.repositories.policy_repository import PolicyRepository
from app.repositories.quote_repository import QuoteRepository
from app.repositories.endorsement_repository import EndorsementRepository
from app.services.policy_service import PolicyService as PolicyServiceLogic

def verify_policy_services():
    db = SessionLocal()
    try:
        print("Starting verification...")
        
        # 1. Setup Data
        company = db.query(Company).first()
        if not company:
            print("No company found.")
            return

        user = db.query(User).filter(User.company_id == company.id).first()
        if not user:
            print("No user found.")
            return

        client = db.query(Client).filter(Client.company_id == company.id).first()
        if not client:
            # Create dummy client
            client = Client(
                company_id=company.id,
                first_name="Test",
                last_name="Client",
                email=f"test{uuid.uuid4()}@example.com",
                created_by=user.id
            )
            db.add(client)
            db.commit()

        policy_type = db.query(PolicyType).filter(PolicyType.company_id == company.id).first()
        if not policy_type:
            policy_type = PolicyType(
                company_id=company.id,
                name="Test Type",
                code="TST",
                created_by=user.id
            )
            db.add(policy_type)
            db.commit()

        # 2. Create Policy Service
        svc_name = f"Test Service {uuid.uuid4()}"
        service = PolicyServiceModel(
            company_id=company.id,
            name_en=svc_name,
            default_price=Decimal("100.00"),
            is_active=True
        )
        db.add(service)
        db.commit()
        print(f"Created Service: {service.name_en} (ID: {service.id})")

        # 3. Create Policy with Service
        repo = PolicyRepository(db)
        quote_repo = QuoteRepository(db)
        endorsement_repo = EndorsementRepository(db)
        logic = PolicyServiceLogic(repo, quote_repo, endorsement_repo)

        print("Creating Policy with Service...")
        policy = logic.create_policy(
            company_id=company.id,
            client_id=client.id,
            policy_type_id=policy_type.id,
            coverage_amount=Decimal("1000.00"),
            premium_amount=Decimal("200.00"),
            premium_frequency="annual",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            created_by=user.id,
            services=[
                {"service_id": service.id, "price": Decimal("100.00")}
            ]
        )
        
        # 4. Verify Association
        print(f"Policy Created: {policy.policy_number} (ID: {policy.id})")
        
        # Check services
        if policy.services:
            print(f"Policy has {len(policy.services)} services.")
            found = False
            for s in policy.services:
                print(f" - Service: {s.name_en}")
                if s.id == service.id:
                    found = True
            
            if found:
                print("SUCCESS: Service found linked to policy.")
            else:
                print("FAILURE: Service not found in policy.services.")
        else:
            print("FAILURE: Policy has no services.")

        # Check association table for price
        assoc = db.query(policy_service_association).filter_by(
            policy_id=policy.id,
            service_id=service.id
        ).first()

        if assoc:
            print(f"Association Price: {assoc.price}")
            if assoc.price == Decimal("100.00"):
                print("SUCCESS: Price recorded correctly.")
            else:
                print(f"FAILURE: Price mismatch. Expected 100.00, got {assoc.price}")
        else:
            print("FAILURE: Association record not found.")

        # Cleanup
        db.delete(policy)
        db.delete(service)
        db.commit()
        print("Cleanup complete.")

    except Exception as e:
        print(f"Verification Failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    verify_policy_services()
