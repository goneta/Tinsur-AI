"""
API endpoints for policy document archive and verification.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.services.archive_service import ArchiveService

router = APIRouter()

@router.get("/policies/{policy_id}/history")
def get_archive_history(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get history of archived document versions for a policy."""
    service = ArchiveService(db)
    return service.get_archives_for_policy(policy_id)

@router.post("/verify", response_model=dict)
async def verify_document(
    policy_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify the integrity of a policy document.
    Checks if the uploaded file matches the archived hash.
    """
    content = await file.read()
    service = ArchiveService(db)
    
    is_valid, archive = service.verify_document_integrity(policy_id, content)
    
    if is_valid:
        return {
            "status": "valid",
            "message": "Document integrity verified. Legally authentic.",
            "archived_at": archive.archived_at,
            "version": archive.archive_version,
            "hash": archive.document_hash
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document integrity check failed. The file may have been tampered with or is not the correct version."
        )
