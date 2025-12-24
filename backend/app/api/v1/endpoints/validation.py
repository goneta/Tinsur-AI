from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, Dict
from pydantic import BaseModel
import uuid
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.quote import Quote
from app.models.policy import Policy
from app.models.claim import Claim
from app.models.client_details import ClientAutomobile, ClientHousing, ClientHealth, ClientLife
from app.repositories.quote_repository import QuoteRepository
from app.repositories.policy_repository import PolicyRepository
from app.repositories.claim_repository import ClaimRepository

router = APIRouter()

class ValidationRequest(BaseModel):
    type: str # 'quote', 'policy', 'claim'
    data: Dict[str, Any]

@router.post("/validate")
def validate_entity(
    request: ValidationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate and persist an entity created by an AI agent.
    """
    try:
        data = request.data
        if request.type == 'quote':
            repo = QuoteRepository(db)
            
            # Simple mapping from agent output to model
            # In a real app, we would use a more robust mapper or service
            quote = Quote(
                company_id=current_user.company_id,
                client_id=data.get('client_id') or current_user.id,
                # For demo, use a default policy type if not provided
                policy_type_id=data.get('policy_type_id') or UUID('e640307e-3245-424a-950e-797745778a87'), # Example/Demo UUID
                quote_number=data.get('quote_number', f"Q-{uuid.uuid4().hex[:8].upper()}"),
                coverage_amount=data.get('premium_amount', 0), # Simplified
                premium_amount=data.get('premium_amount', 0),
                final_premium=data.get('premium_amount', 0),
                status='accepted',
                details=data,
                created_by=current_user.id,
                valid_until=date.today() + timedelta(days=30)
            )
            saved = repo.create(quote)
            
            # Upsert into policy-specific detail tables
            client_id = quote.client_id
            policy_type = data.get('policy_type', '').lower()
            
            if 'auto' in policy_type:
                # Check for existing record
                detail = db.query(ClientAutomobile).filter(ClientAutomobile.client_id == client_id).first()
                if not detail:
                    detail = ClientAutomobile(client_id=client_id)
                    db.add(detail)
                
                detail.vehicle_value = data.get('vehicle_value')
                detail.vehicle_age = data.get('vehicle_age')
                detail.vehicle_mileage = data.get('vehicle_mileage')
                detail.vehicle_registration = data.get('vehicle_registration')
                detail.license_number = data.get('license_number')
                
                # DOB handle
                dob_str = data.get('driver_dob')
                if dob_str:
                    try:
                        detail.driver_dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
                    except:
                        pass
                
                db.commit()

            elif 'hous' in policy_type or 'home' in policy_type:
                detail = db.query(ClientHousing).filter(ClientHousing.client_id == client_id).first()
                if not detail:
                    detail = ClientHousing(client_id=client_id)
                    db.add(detail)
                # Future: map housing-specific fields from data
                db.commit()

            elif 'health' in policy_type:
                detail = db.query(ClientHealth).filter(ClientHealth.client_id == client_id).first()
                if not detail:
                    detail = ClientHealth(client_id=client_id)
                    db.add(detail)
                db.commit()


            elif 'life' in policy_type:
                detail = db.query(ClientLife).filter(ClientLife.client_id == client_id).first()
                if not detail:
                    detail = ClientLife(client_id=client_id)
                    db.add(detail)
                db.commit()

            return {"status": "success", "id": str(saved.id), "type": "quote"}
            
        elif request.type == 'policy':
             repo = PolicyRepository(db)
             policy = Policy(
                 company_id=current_user.company_id,
                 client_id=data.get('client_id') or current_user.id,
                 policy_number=data.get('policy_number', f"P-{uuid.uuid4().hex[:8].upper()}"),
                 premium_amount=data.get('premium_amount', 0),
                 start_date=date.today(),
                 end_date=date.today() + timedelta(days=365),
                 status='active',
                 details=data,
                 created_by=current_user.id
             )
             saved = repo.create(policy)
             return {"status": "success", "id": str(saved.id), "type": "policy"}
             
        elif request.type == 'claim':
             repo = ClaimRepository(db)
             # Basic claim creation
             claim = Claim(
                 company_id=current_user.company_id,
                 client_id=data.get('client_id') or current_user.id,
                 policy_id=data.get('policy_id') or UUID('00000000-0000-0000-0000-000000000000'), # Need real policy
                 claim_number=data.get('claim_number', f"C-{uuid.uuid4().hex[:8].upper()}"),
                 incident_date=date.today(),
                 incident_description=data.get('incident_description', 'Validated via AI Assistant'),
                 claim_amount=data.get('claim_amount', 0),
                 status='submitted'
             )
             saved = repo.create(claim)
             return {"status": "success", "id": str(saved.id), "type": "claim"}
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported entity type")
            
    except Exception as e:
        import traceback
        print(f"Validation Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
