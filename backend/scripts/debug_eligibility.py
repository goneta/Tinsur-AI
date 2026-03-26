import sys
import os
from uuid import UUID

# Add the parent directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.premium_policy_service import PremiumPolicyService
from app.models.client import Client
from app.models.user import User
from app.models.company import Company
from app.schemas.premium_policy import PremiumPolicyMatchResponse
from fastapi.encoders import jsonable_encoder

def debug_eligibility():
    db = SessionLocal()
    try:
        print("--- Starting Eligibility Debug ---")
        
        # 1. Get a Company
        company = db.query(Company).first()
        if not company:
            print("ERROR: No company found.")
            return
        print(f"Using Company: {company.name} ({company.id})")

        # 2. Get a Client (Assuming we have one, getting the first one)
        client = db.query(Client).filter(Client.company_id == company.id).first()
        if not client:
             print("ERROR: No client found for this company.")
             return
        
        print(f"Using Client: {client.first_name} {client.last_name} ({client.id})")
        print(f"Client Data: DOB={client.date_of_birth}, Acc={client.accident_count}, Income={client.annual_income}", flush=True)

        # Temporary: Update client if fields are missing for testing
        if not client.date_of_birth or not client.annual_income:
             print("UPDATE: Setting temporary test data for Client...", flush=True)
             from datetime import date
             client.date_of_birth = date(1980, 1, 1)
             client.annual_income = 50000
             client.employment_status = "Employed"
             db.commit()

        # 3. Run Matching Service
        service = PremiumPolicyService(db)
        
        try:
            result = service.match_eligible_policies(company.id, client.id)
            print("\n--- Result ---", flush=True)
            print(f"Status: {result.get('status')}", flush=True)
            print(f"Message: {result.get('message')}", flush=True)
            
            # TEST SERIALIZATION
            print("Testing Serialization...", flush=True)
            # Simulate what FastAPI does:
            # 1. Validate with Pydantic model
            pydantic_model = PremiumPolicyMatchResponse(**result)
            print("Pydantic Validation Successful!", flush=True)
            
            # 2. Encode to JSON
            encoded = jsonable_encoder(pydantic_model)
            print("JSON Encoding Successful!", flush=True)
            print(">>> SUCCESS: SERIALIZATION WORKING <<<", flush=True)

            
            if result.get('status') == 'missing_info':
                print(f"Missing Fields: {result.get('missing_fields')}")
            
            if result.get('status') == 'success':
                eligible_policies = result.get('data', [])
                print(f"Eligible Policies Count: {len(eligible_policies)}")
                for p in eligible_policies:
                    print(f" - {p.name} (Price: {p.price})")
                
                print(f"Recommended ID: {result.get('recommended_id')}")
                
        except Exception as e:
            print(f"\nCRITICAL EXCEPTION during match_eligible_policies: {e}")
            import traceback
            traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    debug_eligibility()
