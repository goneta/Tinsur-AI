
import os
import sys
import uuid
import json
from google.adk.tools import tool
from typing import Optional, Dict, Any, List
import sqlalchemy

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
        
        # Convert SQLAlchemy objects to dict for JSON serialization
        if "data" in match_result:
            match_result["eligible_policies"] = [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "description": p.description,
                    "estimated_premium": float(p.price)
                } for p in match_result["data"]
            ]
            del match_result["data"] # Remove non-serializable objects
            
        if "recommended_id" in match_result and match_result["recommended_id"]:
            match_result["recommended_id"] = str(match_result["recommended_id"])
            
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

@tool
def search_clients(query: str, company_id: str) -> str:
    """
    Searches for clients by name, email, or phone.
    Returns a list of matching clients with their IDs.
    """
    print(f"DEBUG: search_clients called with query: {query}")
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if backend_root not in sys.path: sys.path.append(backend_root)
    
    try:
        from app.core.database import SessionLocal
        from app.models.client import Client
        from sqlalchemy import or_
        
        db = SessionLocal()
        search_filter = or_(
            Client.first_name.ilike(f"%{query}%"),
            Client.last_name.ilike(f"%{query}%"),
            Client.email.ilike(f"%{query}%"),
            Client.phone.ilike(f"%{query}%")
        )
        
        clients = db.query(Client).filter(
            Client.company_id == uuid.UUID(company_id),
            search_filter
        ).limit(5).all()
        
        results = [
            {
                "id": str(c.id),
                "name": f"{c.first_name} {c.last_name}",
                "email": c.email,
                "phone": c.phone
            } for c in clients
        ]
        
        return json.dumps(results)
    except Exception as e:
        return f"Error searching clients: {str(e)}"
    finally:
        db.close()

@tool
def list_recent_clients(company_id: str) -> str:
    """
    Lists the most recently updated clients in the organization.
    Useful for quickly picking a client the user might be working with.
    """
    print(f"DEBUG: list_recent_clients called")
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if backend_root not in sys.path: sys.path.append(backend_root)
    
    try:
        from app.core.database import SessionLocal
        from app.models.client import Client
        
        db = SessionLocal()
        clients = db.query(Client).filter(
            Client.company_id == uuid.UUID(company_id)
        ).order_by(Client.updated_at.desc()).limit(5).all()
        
        results = [
            {
                "id": str(c.id),
                "name": f"{c.first_name} {c.last_name}",
                "email": c.email
            } for c in clients
        ]
        
        return json.dumps(results)
    except Exception as e:
        return f"Error listing clients: {str(e)}"
    finally:
        db.close()
