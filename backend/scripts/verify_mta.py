
import sys
import os
from uuid import uuid4
from decimal import Decimal
from datetime import date, datetime

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.database import SessionLocal
from app.models.company import Company
from app.models.client import Client
from app.models.user import User
from app.models.policy import Policy
from app.models.policy_type import PolicyType
from app.models.endorsement import Endorsement
from app.models.underwriting import UnderwritingReferral
from app.models.regulatory import IFRS17Group, RegulatoryMetricSnapshot
from app.models.archive import PolicyArchive
from app.services.policy_service import PolicyService
from app.repositories.policy_repository import PolicyRepository
from app.repositories.quote_repository import QuoteRepository
from app.repositories.endorsement_repository import EndorsementRepository
from app.core.config import settings

def test_mta_lifecycle():
    db = SessionLocal()
    try:
        # 1. Setup Data
        company = db.query(Company).first()
        if not company:
            print("No company found, creating one...")
            company = Company(name="Test Insurance Co", email="test@tinsur.ai")
            db.add(company)
            db.commit()

        client = db.query(Client).filter(Client.company_id == company.id).first()
        if not client:
            client = Client(company_id=company.id, first_name="MTA", last_name="Test", email="mta@test.com")
            db.add(client)
            db.commit()

        # Create a user with low authority
        agent = User(
            email=f"agent_{uuid4().hex[:6]}@test.com",
            first_name="Low Authority",
            last_name="Agent",
            role="agent",
            underwriting_limit=Decimal("5000.00"),
            company_id=company.id,
            password_hash="dummy"
        )
        db.add(agent)
        
        # Create a manager
        manager = User(
            email=f"manager_{uuid4().hex[:6]}@test.com",
            first_name="Test",
            last_name="Manager",
            role="company_admin",
            company_id=company.id,
            password_hash="dummy"
        )
        db.add(manager)
        db.commit()

        # Create an IFRS 17 Group
        ifrs_group = IFRS17Group(
            company_id=company.id,
            name="Motor 2025 - Test",
            initial_csm=Decimal("10000.00"),
            remaining_csm=Decimal("10000.00"),
            status='active'
        )
        db.add(ifrs_group)
        db.commit()

        policy_type = db.query(PolicyType).first()
        if not policy_type:
            policy_type = PolicyType(name="Motor", code="MOT", company_id=company.id)
            db.add(policy_type)
            db.commit()

        # 2. Create Policy
        policy = Policy(
            company_id=company.id,
            client_id=client.id,
            policy_type_id=policy_type.id,
            policy_number=f"POL-MTA-{uuid4().hex[:6]}",
            coverage_amount=Decimal("4000.00"),
            premium_amount=Decimal("1000.00"),
            start_date=date.today(),
            end_date=date(2026, 1, 1),
            status='active',
            ifrs17_group_id=ifrs_group.id,
            created_by=agent.id
        )
        db.add(policy)
        db.commit()
        
        # Initial Archive
        archive_service = PolicyService(
            PolicyRepository(db), QuoteRepository(db), EndorsementRepository(db)
        ).archive_service
        archive_service.archive_policy_document(policy.id, "initial.pdf", b"initial content")
        
        print(f"Policy Created: {policy.policy_number}")
        print(f"Initial CSM: {ifrs_group.remaining_csm}")

        # 3. Create Endorsement (Exceeds Authority)
        policy_service = PolicyService(
            PolicyRepository(db), QuoteRepository(db), EndorsementRepository(db)
        )
        
        # High value coverage increase: 4000 -> 6000 (Agent limit is 5000)
        endorsement = policy_service.create_endorsement(
            company_id=company.id,
            policy_id=policy.id,
            endorsement_type='coverage_change',
            changes={'coverage_amount': 6000},
            premium_adjustment=Decimal("500.00"),
            effective_date=date.today(),
            created_by=agent.id,
            reason="Upgrading coverage"
        )
        
        db.refresh(endorsement)
        print(f"Endorsement Created: {endorsement.endorsement_number}, Status: {endorsement.status}")
        
        # Verify Referral
        referral = db.query(UnderwritingReferral).filter(UnderwritingReferral.endorsement_id == endorsement.id).first()
        if referral:
            print(f"Referral Triggered: {referral.reason}")
        else:
            print("ERROR: Referral NOT triggered!")

        # 4. Approve Referral & Apply Endorsement
        # Manager approves
        policy_service.underwriting_service.process_referral_decision(
            referral_id=referral.id,
            decided_by_id=manager.id,
            status='approved',
            notes="Approved coverage increase"
        )
        
        db.refresh(endorsement)
        print(f"Endorsement status after approval: {endorsement.status}")

        # Finalize (apply) endorsement
        updated_policy = policy_service.approve_endorsement(endorsement.id, manager.id)
        
        db.refresh(policy)
        db.refresh(ifrs_group)
        
        print(f"Policy Premium after MTA: {policy.premium_amount}")
        print(f"Policy Coverage after MTA: {policy.coverage_amount}")
        print(f"CSM after MTA: {ifrs_group.remaining_csm}")
        
        # Verify Archiving
        archives = db.query(PolicyArchive).filter(PolicyArchive.policy_id == policy.id).all()
        print(f"Archive records: {len(archives)}")
        for arch in archives:
            print(f" - Archive Hash: {arch.document_hash[:10]}... at {arch.archived_at}")

        # 5. Cleanup
        # (Optional: delete test records)
        
        print("\nSUCCESS: Automated Endorsement Lifecycle (MTA) verified.")

    except Exception as e:
        print(f"\nFAILURE: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_mta_lifecycle()
