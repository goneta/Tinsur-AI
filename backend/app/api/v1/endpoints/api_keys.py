from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import secrets
import hashlib

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_admin
from app.models.user import User
from app.models.api_keys import ApiKey
from app.schemas.api_keys import ApiKeyCreate, ApiKeyResponse, ApiKeyCreatedResponse, ApiKeyUpdate

router = APIRouter()

def generate_api_key():
    """Generate a secure API key and its hash."""
    prefix = "sk_live_"
    # 32 bytes of randomness -> ~43 chars in base64/urlsafe
    key_part = secrets.token_urlsafe(32)
    full_key = f"{prefix}{key_part}"
    
    # Hash the key for storage
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    return full_key, key_hash, prefix

@router.post("/", response_model=ApiKeyCreatedResponse)
def create_api_key(
    key_in: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Create a new API key.
    Only admins can create API keys.
    The plain text key is returned ONLY once.
    """
    plain_key, key_hash, prefix = generate_api_key()
    
    db_key = ApiKey(
        name=key_in.name,
        key_hash=key_hash,
        key_prefix=prefix[:10], # Store enough to identify logic type or just first chars
        agent_id=key_in.agent_id,
        expires_at=key_in.expires_at,
        is_active=True
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    
    # Construct response with the plain key
    return ApiKeyCreatedResponse(
        id=db_key.id,
        name=db_key.name,
        key_prefix=db_key.key_prefix,
        agent_id=db_key.agent_id,
        is_active=db_key.is_active,
        created_at=db_key.created_at,
        expires_at=db_key.expires_at,
        last_used_at=db_key.last_used_at,
        plain_text_key=plain_key
    )

@router.get("/", response_model=List[ApiKeyResponse])
def list_api_keys(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List all API keys."""
    keys = db.query(ApiKey).offset(skip).limit(limit).all()
    return keys

@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_api_key(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Revoke (delete) an API key."""
    key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API Key not found")
    
    db.delete(key)
    db.commit()

@router.put("/{key_id}", response_model=ApiKeyResponse)
def update_api_key(
    key_id: str,
    key_in: ApiKeyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update an API Key (e.g. rename, deactivate)."""
    key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API Key not found")
        
    if key_in.name is not None:
        key.name = key_in.name
    if key_in.is_active is not None:
        key.is_active = key_in.is_active
    if key_in.agent_id is not None:
        key.agent_id = key_in.agent_id
        
    db.commit()
    db.refresh(key)
    return key
