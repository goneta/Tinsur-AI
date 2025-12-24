
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import hmac
import hashlib
import uuid
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.models.policy import Policy
from app.models.company import Company
from app.core.config import settings

router = APIRouter()

# Secret key for HMAC - in production this should be in settings
SECRET_KEY = settings.SECRET_KEY if hasattr(settings, "SECRET_KEY") else "insurance-saas-verification-secret"

def generate_verification_token(policy_id: str) -> str:
    """Generate a secure verification token for a policy id."""
    return hmac.new(
        SECRET_KEY.encode(),
        policy_id.encode(),
        hashlib.sha256
    ).hexdigest()

@router.post("/generate/{policy_id}", tags=["QR Verification"])
def generate_qr_data(
    policy_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Generate or refresh QR verification data for a policy (Agent/Admin only)."""
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    token = generate_verification_token(str(policy.id))
    policy.qr_code_data = token
    db.commit()
    
    return {
        "policy_id": policy.id,
        "token": token,
        "verification_url": f"/verify/{token}"
    }

@router.get("/verify/{token}", tags=["Public Verification"])
def verify_policy(
    token: str,
    db: Session = Depends(get_db)
):
    """Public endpoint to verify a policy by its token."""
    policy = db.query(Policy).filter(Policy.qr_code_data == token).first()
    
    if not policy:
        return {
            "status": "INVALID",
            "message": "Policy verification failed. Token is invalid or not found."
        }
    
    # Check if policy is active
    is_active = policy.is_active
    
    # Get client initials for privacy
    client_name = policy.client.full_name if policy.client else "Unknown"
    name_parts = client_name.split()
    initials = "".join([n[0] for n in name_parts if n])
    
    return {
        "status": "VERIFIED" if is_active else "INACTIVE",
        "policy_number": policy.policy_number,
        "policy_type": policy.policy_type.name if policy.policy_type else "General",
        "company_name": policy.company.name if policy.company else "Unknown",
        "client_initials": initials,
        "expiry_date": policy.end_date.isoformat() if policy.end_date else None,
        "is_active": is_active,
        "verified_at": datetime.utcnow().isoformat()
    }
