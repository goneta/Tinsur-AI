"""
KYC and Identity Verification endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from uuid import UUID
import os
import shutil

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.ai_service import AiService
from app.models.client import Client
from app.models.user import User

router = APIRouter()

async def get_optional_user(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
) -> Optional[User]:
    try:
        return await get_current_user(None, db) # This won't work easily with Depends(security)
    except:
        return None

# Simplified optional dependency or just use a helper
def get_user_if_authenticated(db: Session = Depends(get_db)):
    # Manual check since HTTPBearer raises 403 on missing token
    pass

@router.post("/parse-document")
async def parse_document(
    image_url: str = Body(..., embed=True),
    doc_type: str = Body("identity_document", embed=True),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Parses a document image using AI and returns extracted fields.
    Publicly accessible to support registration portal, but uses company context if logged in.
    """
    ai_service = AiService(db)
    company_id = str(current_user.company_id) if current_user else None
    results = await ai_service.parse_kyc_document(image_url, doc_type, company_id=company_id)
    
    if "error" in results:
        raise HTTPException(status_code=400, detail=results["error"])
        
    return results

@router.post("/upload-and-parse")
async def upload_and_parse(
    file: UploadFile = File(...),
    doc_type: str = Form("identity_document"),
    client_id: Optional[UUID] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Uploads a file and immediately parses it.
    Publicly accessible to support registration portal auto-fill.
    """
    # Create kyc uploads dir
    kyc_dir = os.path.join("uploads", "kyc")
    if not os.path.exists(kyc_dir):
        os.makedirs(kyc_dir)
        
    file_path = os.path.join(kyc_dir, f"{str(UUID(int=0))}_{file.filename}") # Simple unique name for temp
    # Better unique name
    import uuid
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(kyc_dir, f"{file_id}{ext}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Construct URL for AiService (AiService might need a local path option but URL is fine if it can reach its own localhost)
    # Actually, AiService uses requests.get. Let's make it handle local paths too or use local url.
    # For simplicity, we'll pass the local path to a new service method or update parse_kyc_document.
    
    ai_service = AiService(db)
    
    # We'll pass the file content directly to avoid URL issues during local dev
    with open(file_path, "rb") as f:
        image_data = f.read()
        
    company_id = str(current_user.company_id) if current_user else None
    results = await ai_service.parse_kyc_document_bytes(image_data, doc_type, company_id=company_id)
    
    if "error" in results:
        raise HTTPException(status_code=400, detail=results["error"])
        
    relative_path = file_path.replace("\\", "/")
    
    # Auto-update client record if client_id is provided
    if client_id:
        from app.models.client_details import ClientAutomobile
        client = db.query(Client).filter(Client.id == client_id).first()
        if client:
            if doc_type == "car_papers":
                auto = db.query(ClientAutomobile).filter(ClientAutomobile.client_id == client_id).first()
                if not auto:
                    auto = ClientAutomobile(client_id=client_id)
                    db.add(auto)
                auto.registration_document_url = relative_path
                # We can also decide to auto-fill here, but frontend usually handles it for UX
            elif doc_type == "identity_document":
                client.id_card_url = relative_path
            elif doc_type == "driving_license":
                client.driving_license_url = relative_path
            
            db.commit()
        
    return {
        **results,
        "file_path": relative_path
    }

@router.post("/verify/{client_id}")
async def verify_client_kyc(
    client_id: UUID,
    status: str = Body(..., embed=True), # verified, rejected
    notes: Optional[str] = Body(None, embed=True),
    results: Dict[str, Any] = Body({}, embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates the KYC status for a client after AI or manual review.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    if client.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    client.kyc_status = status
    client.kyc_notes = notes
    if results:
        client.kyc_results = results
        
    db.commit()
    return {"message": f"Client KYC status updated to {status}"}

@router.get("/status/{client_id}")
async def get_kyc_status(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Gets the detailed KYC status and analysis results for a client.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    return {
        "status": client.kyc_status,
        "notes": client.kyc_notes,
        "results": client.kyc_results,
        "updated_at": client.updated_at
    }
