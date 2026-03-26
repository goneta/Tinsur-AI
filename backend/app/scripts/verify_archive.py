
import sys
import os
import asyncio
from uuid import UUID

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal, engine, Base
from app.models.policy import Policy
from app.models.archive import PolicyArchive
from app.services.archive_service import ArchiveService
from app.models.company import Company

async def verify_document_archive():
    print("Ensuring Archive tables exist...")
    Base.metadata.create_all(bind=engine)
    
    print("Verifying Immutable Document Archive Flow...")
    db = SessionLocal()
    try:
        company = db.query(Company).first()
        if not company:
            print("No company found for testing.")
            return

        # 1. Setup a dummy policy
        policy = db.query(Policy).filter(Policy.company_id == company.id).first()
        if not policy:
            print("No policy found for testing (needed for document link).")
            # Create a quick dummy if not exists
            from app.models.client import Client
            from app.models.policy_type import PolicyType
            from decimal import Decimal
            from datetime import date
            import uuid
            
            client = db.query(Client).first()
            pt = db.query(PolicyType).first()
            policy = Policy(
                company_id=company.id,
                client_id=client.id if client else None,
                policy_type_id=pt.id if pt else None,
                policy_number=f"POL-ARCH-{uuid.uuid4().hex[:6]}",
                premium_amount=Decimal("100"),
                coverage_amount=Decimal("1000"),
                start_date=date.today(),
                end_date=date.today(),
                policy_document_url="https://storage.tinsur.ai/policies/P-123.pdf"
            )
            db.add(policy)
            db.commit()
            print(f"Created dummy policy: {policy.policy_number}")

        print(f"Testing for Policy: {policy.policy_number}")
        
        # 2. Archive a "Document"
        archive_service = ArchiveService(db)
        original_content = b"This is the original policy document content. Legally binding."
        
        print("Archiving original document...")
        archive = archive_service.archive_policy_document(
            policy_id=policy.id,
            document_url="https://storage.tinsur.ai/policies/original.pdf",
            file_content=original_content
        )
        
        print(f"Archive Created. Hash: {archive.document_hash}")
        
        # 3. Verify Integrity (Success case)
        print("\nVerifying integrity with SAME content...")
        is_valid, record = archive_service.verify_document_integrity(policy.id, original_content)
        print(f"Verification Result: {'VALID' if is_valid else 'FAILED'}")
        
        if not is_valid:
            print("ERROR: Verification should have passed.")

        # 4. Verify Integrity (Failure case - Tampered)
        tampered_content = b"This is the original policy document content. Legally BINDING." # Changed 'binding' to 'BINDING'
        print("\nVerifying integrity with TAMPERED content...")
        is_valid, record = archive_service.verify_document_integrity(policy.id, tampered_content)
        print(f"Verification Result: {'VALID' if is_valid else 'TAMPERED'}")
        
        if is_valid:
            print("ERROR: Verification should have failed for tampered content.")
        else:
            print("SUCCESS: System correctly identified the tampered file.")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(verify_document_archive())
