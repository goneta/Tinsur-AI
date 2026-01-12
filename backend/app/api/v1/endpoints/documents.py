
from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from uuid import UUID
import uuid
import os
import shutil
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentLabel
from app.models.inter_company_share import InterCompanyShare
from app.models.company import Company
from app.repositories.policy_repository import PolicyRepository
from app.services.document_service import document_service
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# Schema Models
class DocumentResponse(BaseModel):
    id: UUID
    name: str
    label: str
    fileType: str
    size: str
    visibility: str
    owner: str
    date: str
    scope: Optional[str] = None
    
    class Config:
        orm_mode = True

class ShareRequest(BaseModel):
    visibility: str # PUBLIC, PRIVATE
    scope: Optional[str] = None # B2B, B2C, etc
    is_shareable: bool
    reshare_rule: Optional[str] = None # A, B, C

# Simple absolute path relative to project root
# Assuming we are in backend/app/api/v1/endpoints
# backend/uploads
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def format_doc(doc: Document, owner_name_override: str = None, scope: str = None) -> Dict[str, Any]:
    """Helper to format document for frontend with safety checks."""
    try:
        # File Size safety
        try:
            raw_size = doc.file_size
            if isinstance(raw_size, str):
                raw_size = int(raw_size)
            size_mb = (raw_size or 0) / 1024 / 1024
        except:
            size_mb = 0

        # Date safety
        try:
            if doc.created_at:
                if isinstance(doc.created_at, str):
                    # Handle string dates from SQLite
                    date_val = datetime.fromisoformat(doc.created_at.replace('Z', '+00:00'))
                    date_str = date_val.strftime("%Y-%m-%d")
                else:
                    date_str = doc.created_at.strftime("%Y-%m-%d")
            else:
                date_str = datetime.utcnow().strftime("%Y-%m-%d")
        except:
            date_str = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Determine owner
        owner = owner_name_override
        if not owner:
            try:
                if doc.company:
                    owner = doc.company.name
                else:
                    owner = "Me"
            except:
                owner = "System"

        # Label safety
        try:
            label_val = doc.label
            if hasattr(label_val, 'value'):
                label_str = str(label_val.value)
            else:
                label_str = str(label_val)
        except:
            label_str = "Document"

        return {
            "id": str(doc.id),
            "name": doc.name or "Unnamed Document",
            "label": label_str,
            "fileType": doc.file_type or "unknown",
            "size": f"{size_mb:.2f} MB",
            "visibility": doc.visibility or "PRIVATE",
            "owner": owner,
            "date": date_str,
            "scope": scope or doc.scope or "B2B",
            "isShareable": bool(doc.is_shareable),
            "reshareRule": doc.reshare_rule or "C"
        }
    except Exception as e:
        logger.error(f"FATAL error formatting document {getattr(doc, 'id', 'unknown')}: {str(e)}")
        return {
            "id": str(getattr(doc, 'id', 'error')),
            "name": "Error loading document",
            "label": "Error",
            "fileType": "unknown",
            "size": "0.00 MB",
            "visibility": "PRIVATE",
            "owner": "Unknown",
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
        }

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    label: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Create a safe unique filename
        file_uuid = uuid.uuid4()
        ext = os.path.splitext(file.filename)[1]
        safe_filename = f"{file_uuid}{ext}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Save file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create DB Entry
        new_doc = Document(
            company_id=current_user.company_id,
            uploaded_by=current_user.id,
            name=file.filename,
            file_url=f"/uploads/{safe_filename}", 
            file_type=file.filename.split('.')[-1].lower(),
            file_size=file_size,
            label=label,
            visibility='PRIVATE',
            scope='B2B'
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        
        return {
            "status": "success", 
            "document": format_doc(new_doc, "Me"),
            "url": new_doc.file_url
        }
    except Exception as e:
        logger.exception("Upload failed")
        raise HTTPException(status_code=500, detail=f"Upload Error: {str(e)}")

@router.get("/list")
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # 1. My Documents
        my_docs = db.query(Document).filter(Document.company_id == current_user.company_id).all()
        
        # 3. Shared With Me
        shared_docs = []
        
        # A. Explicit Shares (InterCompanyShare)
        # We need to eager load document and from_company to avoid late session issues
        shares = db.query(InterCompanyShare).filter(
            (InterCompanyShare.to_company_id == current_user.company_id) |
            (InterCompanyShare.to_user_id == current_user.id)
        ).filter(InterCompanyShare.is_revoked == False).all()
        
        for share in shares:
            if share.document:
                shared_docs.append({
                    "doc": share.document,
                    "scope": share.scope,
                    "owner": share.from_company.name if share.from_company else "Partner"
                })
                
        # B. Broadcast Logic
        broadcast_query = db.query(Document).filter(
            Document.company_id != current_user.company_id,
            Document.visibility == 'PRIVATE'
        )
        
        if current_user.role == 'client':
            broadcast_query = broadcast_query.filter(Document.scope == 'B2C')
        else:
            broadcast_query = broadcast_query.filter(Document.scope.in_(['B2B', 'B2C']))
            
        broadcast_docs = broadcast_query.all()
        
        for doc in broadcast_docs:
            if not any(d['doc'].id == doc.id for d in shared_docs):
                shared_docs.append({
                    "doc": doc,
                    "scope": doc.scope,
                    "owner": doc.company.name if doc.company else "Network Partner"
                })

        # 2. Public Documents
        public_docs = db.query(Document).filter(
            Document.visibility == 'PUBLIC',
            Document.company_id != current_user.company_id
        ).all()

        return {
            "my_docs": [format_doc(d, "Me") for d in my_docs],
            "public_docs": [format_doc(d) for d in public_docs],
            "shared_with_me": [format_doc(s['doc'], s['owner'], s['scope']) for s in shared_docs]
        }
    except Exception as e:
        logger.exception("Failed to list documents")
        raise HTTPException(status_code=500, detail=f"Failed to fetch documents: {str(e)}")

@router.post("/{doc_id}/share")
async def update_share_settings(
    doc_id: UUID,
    settings: ShareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    if doc.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    doc.visibility = settings.visibility
    doc.scope = settings.scope
    doc.is_shareable = settings.is_shareable
    doc.reshare_rule = settings.reshare_rule
    
    db.commit()
    return {"status": "success", "message": "Settings updated"}


@router.get("/policy/{policy_id}", response_model=List[str])
def list_policy_documents(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List auto-generated insurance documents for a specific policy."""
    repo = PolicyRepository(db)
    policy = repo.get_by_id(policy_id)
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
        
    # Access Control: Company or Client
    if policy.company_id != current_user.company_id:
         # Check if client
         if str(current_user.id) != str(policy.client_id):
             raise HTTPException(status_code=403, detail="Not authorized")

    doc_dir = os.path.join(document_service.output_dir, str(policy_id))
    if not os.path.exists(doc_dir):
        return []

    files = []
    for f in os.listdir(doc_dir):
        if f.endswith(".html") or f.endswith(".pdf"):
            files.append(f"documents/{policy_id}/{f}")
            
    return files

@router.get("/policy/{policy_id}/{filename}")
def get_policy_document(
    policy_id: UUID,
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Serve a specific auto-generated document."""
    # Access Control
    repo = PolicyRepository(db)
    policy = repo.get_by_id(policy_id)
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if policy.company_id != current_user.company_id:
         if str(current_user.id) != str(policy.client_id):
             raise HTTPException(status_code=403, detail="Not authorized")

    safe_filename = os.path.basename(filename)
    file_path = os.path.join(document_service.output_dir, str(policy_id), safe_filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document not found")
        
    return FileResponse(file_path)
