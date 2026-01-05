
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from uuid import UUID
import os
import shutil
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentLabel
from app.models.inter_company_share import InterCompanyShare
from app.models.company import Company
from pydantic import BaseModel

router = APIRouter()

# Schema Models
class DocumentResponse(BaseModel):
    id: UUID
    name: str
    label: str
    file_type: str
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
    # In real app, might need target list, but for now generic "sharing settings" update
    
# Fix UPLOAD_DIR to be absolute path in backend root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
# backend/app/api/v1/endpoints -> backend/app/api/v1 -> backend/app/api -> backend/app -> backend
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    label: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Save file locally
        file_path = os.path.join(UPLOAD_DIR, f"{datetime.now().timestamp()}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create DB Entry
        new_doc = Document(
            company_id=current_user.company_id,
            uploaded_by=current_user.id,
            name=file.filename,
            file_url=file_path, # Local path for now
            file_type=file.filename.split('.')[-1],
            file_size=file_size,
            label=label,
            visibility='PRIVATE' # Default
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        
        
        # Calculate relative URL for frontend access
        # Filename was generated above: f"{datetime.now().timestamp()}_{file.filename}" which is what we saved
        # But we didn't store that variable separately. Let's fix that.
        
        return {
            "status": "success", 
            "document_id": new_doc.id,
            "url": f"/uploads/{os.path.basename(file_path)}",
            "name": new_doc.name
        }
    except Exception as e:
        import traceback
        traceback.print_exc() # Print full stack trace to console
        print(f"UPLOAD ERROR: {str(e)}") # Print error message
        try:
             # Try to print DB URL from session if possible, masking password
             # This is hacky but needed for debug
             url = str(db.get_bind().url)
             if "password" in url:
                  url = "REDACTED"
             print(f"DB URL: {url}")
        except:
             pass
        raise HTTPException(status_code=500, detail=f"Upload Error: {str(e)}")

@router.get("/list")
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. My Documents
    my_docs = db.query(Document).filter(Document.company_id == current_user.company_id).all()
    
    # 2. Public Documents (exclude own to avoid dupe if I made it public)
    public_docs = db.query(Document).filter(
        Document.visibility == 'PUBLIC',
        Document.company_id != current_user.company_id
    ).all()
    
    # 3. Shared With Me (Broadcast Logic + Explicit Shares)
    shared_docs = []
    
    # A. Explicit Shares (InterCompanyShare)
    shares = db.query(InterCompanyShare).filter(
        (InterCompanyShare.to_company_id == current_user.company_id) |
        (InterCompanyShare.to_user_id == current_user.id)
    ).filter(InterCompanyShare.is_revoked == False).all()
    
    for share in shares:
        if share.document:
            shared_docs.append({
                "doc": share.document,
                "scope": share.scope,
                "owner": share.from_company.name if share.from_company else "Shared"
            })
            
    # B. Broadcast Logic (Based on Document Metadata)
    # Get all PRIVATE documents from OTHER companies where Scope permits access
    # Rule 1: B2B -> Visible to all roles except 'client'
    # Rule 2: B2C -> Visible to all roles
    # Rule 3: B2E -> Visible only to company employees (handled by My Docs usually, 
    #                but if intended for 'Partner Employees' we might need logic. 
    #                Let's assume B2E here means 'Business to Employees of ANY partner' for simplicity 
    #                OR strictly internal. Let's assume Broadcast B2E is Internal-Only, so skipped here.)
    
    broadcast_query = db.query(Document).filter(
        Document.company_id != current_user.company_id,
        Document.visibility == 'PRIVATE'
    )
    
    # Client Restriction
    if current_user.role == 'client':
        # Clients only see B2C
        broadcast_query = broadcast_query.filter(Document.scope == 'B2C')
    else:
        # Business users see B2B and B2C
        broadcast_query = broadcast_query.filter(Document.scope.in_(['B2B', 'B2C']))
        
    broadcast_docs = broadcast_query.all()
    
    for doc in broadcast_docs:
        # Avoid duplicates if already explicitly shared
        if not any(d['doc'].id == doc.id for d in shared_docs):
            shared_docs.append({
                "doc": doc,
                "scope": doc.scope,
                "owner": doc.company.name if doc.company else "Network Partner"
            })

    # Format Responses
    def format_doc(doc, owner_name_override=None, scope=None):
        return {
            "id": doc.id,
            "name": doc.name,
            "label": doc.label,
            "fileType": doc.file_type,
            "size": f"{doc.file_size / 1024 / 1024:.2f} MB",
            "visibility": doc.visibility,
            "owner": owner_name_override or (doc.company.name if doc.company else "Me"),
            "date": doc.created_at.strftime("%Y-%m-%d"),
            "scope": scope
        }

    return {
        "my_docs": [format_doc(d, "Me") for d in my_docs],
        "public_docs": [format_doc(d) for d in public_docs],
        "shared_with_me": [format_doc(s['doc'], s['owner'], s['scope']) for s in shared_docs]
    }

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
        
    # Update Metadata
    doc.visibility = settings.visibility
    doc.scope = settings.scope
    doc.is_shareable = settings.is_shareable
    doc.reshare_rule = settings.reshare_rule
    
    db.commit()
    return {"status": "success", "message": "Settings updated"}

