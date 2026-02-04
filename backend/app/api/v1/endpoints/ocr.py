"""
OCR endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_agent
from app.schemas.ocr import OCRProcessResponse, OCRVerifyRequest
from app.services.ocr_service import OCRService
from app.models.user import User

router = APIRouter()


@router.post("/process", response_model=OCRProcessResponse)
async def process_document(
    document: UploadFile = File(...),
    document_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Process an uploaded document with OCR/AI."""
    if not document:
        raise HTTPException(status_code=400, detail="Document file is required.")

    image_bytes = await document.read()
    service = OCRService(db)
    record = await service.process_document(
        image_bytes=image_bytes,
        company_id=str(current_user.company_id) if current_user.company_id else None,
        document_type=document_type,
    )
    return record


@router.get("/results/{document_id}", response_model=OCRProcessResponse)
def get_ocr_results(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get OCR results by document_id."""
    service = OCRService(db)
    result = service.get_result(document_id)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    return result


@router.post("/verify", response_model=OCRProcessResponse)
def verify_ocr_results(
    payload: OCRVerifyRequest,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db),
):
    """Verify OCR results."""
    service = OCRService(db)
    result = service.verify_result(
        document_id=payload.document_id,
        status=payload.status,
        verified_by=str(current_user.id),
        notes=payload.notes,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    return result
