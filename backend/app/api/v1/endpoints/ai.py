"""
AI endpoints (voice commands, suggestions).
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.client import Client
from app.services.premium_policy_service import PremiumPolicyService

router = APIRouter()


class VoiceCommandRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language: Optional[str] = "fr"


class VoiceCommandResponse(BaseModel):
    intent: str
    response: str
    action: Optional[Dict[str, Any]] = None


@router.post("/voice", response_model=VoiceCommandResponse)
def process_voice_command(
    payload: VoiceCommandRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Process a voice command (text transcript)."""
    text = payload.text.lower()
    intent = "unknown"
    response = "Je n'ai pas compris votre demande. Pouvez-vous reformuler ?"
    action: Optional[Dict[str, Any]] = None

    if "statut" in text and "police" in text:
        intent = "policy_status"
        response = "Je vais vérifier le statut de votre police."
        action = {"type": "navigate", "target": "policies"}
    elif "déclarer" in text or "sinistre" in text or "claim" in text:
        intent = "file_claim"
        response = "D'accord. Je vais lancer le formulaire de déclaration de sinistre."
        action = {"type": "navigate", "target": "claims_new"}
    elif "paiement" in text or "payer" in text:
        intent = "make_payment"
        response = "Je vais vous rediriger vers le paiement."
        action = {"type": "navigate", "target": "payments"}

    return VoiceCommandResponse(intent=intent, response=response, action=action)


@router.get("/suggestions")
def get_policy_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return policy suggestions for the current user/client."""
    if current_user.role == "client":
        client = db.query(Client).filter(Client.user_id == current_user.id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client profile not found")
        if not current_user.company_id:
            return {"status": "no_company", "message": "Client not affiliated with a company yet.", "data": []}
        service = PremiumPolicyService(db)
        return service.match_eligible_policies(company_id=current_user.company_id, client_id=client.id)

    return {"status": "error", "message": "Suggestions are available to clients only.", "data": []}
