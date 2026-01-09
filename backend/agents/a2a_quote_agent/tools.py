
import os
import sys
import uuid
import json
from google.adk.tools import tool
from typing import Optional, Dict, Any

@tool
def get_eligible_policies(client_id: str, company_id: str) -> str:
    """
    Checks which premium policies match the client's profile.
    Returns potential policies or a list of missing information required.
    """
    print(f"DEBUG: get_eligible_policies called for client {client_id}")
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if backend_root not in sys.path: sys.path.append(backend_root)
    
    try:
        from app.core.database import SessionLocal
        from app.services.premium_policy_service import PremiumPolicyService
        
        db = SessionLocal()
        policy_service = PremiumPolicyService(db)
        
        match_result = policy_service.match_eligible_policies(uuid.UUID(company_id), uuid.UUID(client_id))
        
        return json.dumps(match_result)
    except Exception as e:
        return f"Error checking eligibility: {str(e)}"
    finally:
        db.close()

@tool
def update_client_profile(client_id: str, company_id: str, updates_json: str) -> str:
    """
    Updates the client's profile with new information (e.g., accident count, license years).
    updates_json should be a JSON object string with keys like 'accident_count', 'no_claims_years', etc.
    """
    print(f"DEBUG: update_client_profile called for client {client_id}")
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if backend_root not in sys.path: sys.path.append(backend_root)
    
    try:
        from app.core.database import SessionLocal
        from app.models.client import Client
        import json
        
        updates = json.loads(updates_json)
        db = SessionLocal()
        
        client = db.query(Client).filter(
            Client.id == uuid.UUID(client_id),
            Client.company_id == uuid.UUID(company_id)
        ).first()
        
        if not client:
            return "Client not found."
            
        fields_updated = []
        if "accident_count" in updates:
            client.accident_count = int(updates["accident_count"])
            fields_updated.append("accident_count")
        if "no_claims_years" in updates:
            client.no_claims_years = int(updates["no_claims_years"])
            fields_updated.append("no_claims_years")
        if "driving_license_years" in updates:
            client.driving_license_years = int(updates["driving_license_years"])
            fields_updated.append("driving_license_years")
        if "employment_status" in updates:
            client.employment_status = str(updates["employment_status"])
            fields_updated.append("employment_status")
        if "age" in updates:
             # Age is usually calculated from DOB, but for simple wizard we might store it or update DOB
             client.age = int(updates["age"])
             fields_updated.append("age")
            
        db.commit()
        return f"Successfully updated client profile fields: {', '.join(fields_updated)}"
    except Exception as e:
        if db: db.rollback()
        return f"Error updating profile: {str(e)}"
    finally:
        db.close()

@tool
def generate_insurance_quote(client_id: str, company_id: str, policy_type_id: str, coverage_amount: float, duration_months: int = 12, user_id: str = None) -> str:
    """
    Calculates and generates a final insurance quote.
    Returns the quote reference and premium details.
    """
    print(f"DEBUG: generate_insurance_quote called for client {client_id}, policy {policy_type_id}")
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if backend_root not in sys.path: sys.path.append(backend_root)
    
    try:
        from app.core.database import SessionLocal
        from app.models.client import Client
        from app.services.quote_service import QuoteService
        from app.repositories.quote_repository import QuoteRepository
        import uuid
        
        db = SessionLocal()
        
        # 1. Fetch Client for Risk Factors
        client = db.query(Client).filter(Client.id == uuid.UUID(client_id)).first()
        if not client:
            return "Client not found."
            
        # 2. Prepare Risk Factors
        risk_factors = {
            "age": client.age or 30,
            "accident_count": client.accident_count or 0,
            "no_claims_years": client.no_claims_years or 0,
            "driving_license_years": client.driving_license_years or 0,
            "vehicle_value": coverage_amount # simplified
        }
        
        # 3. Calculate
        quote_service = QuoteService(QuoteRepository(db))
        calculation = quote_service.calculate_premium(
            risk_factors=risk_factors,
            duration_months=str(duration_months),
            policy_id=uuid.UUID(policy_type_id),
            company_id=uuid.UUID(company_id)
        )
        
        # 4. Create Quote Record
        quote = quote_service.create_quote(
            company_id=uuid.UUID(company_id),
            client_id=uuid.UUID(client_id),
            policy_type_id=uuid.UUID(policy_type_id),
            coverage_amount=float(coverage_amount),
            risk_factors=risk_factors,
            premium_frequency="annual",
            duration_months=int(duration_months),
            discount_percent=0,
            created_by=uuid.UUID(user_id) if user_id else None
        )
        
        response = {
            "quote_number": quote.quote_number,
            "final_premium": calculation["final_premium"],
            "monthly_installment": calculation["monthly_installment"],
            "base_premium": calculation["base_premium"],
            "risk_score": calculation.get("risk_score", 1.0)
        }
        
        return json.dumps(response)
        
    except Exception as e:
        if db: db.rollback()
        return f"Error generating quote: {str(e)}"
    finally:
        db.close()
