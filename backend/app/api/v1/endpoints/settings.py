"""
Settings API endpoints for user preferences and company settings.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
import shutil
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.settings import Settings
from app.models.company import Company
from app.schemas.settings import (
    UserSettingsResponse,
    UserSettingsUpdate,
    UserSettingsCreate,
)
from app.schemas.company import CompanyResponse, CompanyUpdate

router = APIRouter()


@router.get("/", response_model=UserSettingsResponse)
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's settings."""
    settings = db.query(Settings).filter(Settings.user_id == current_user.id).first()
    
    if not settings:
        # Create default settings for user
        settings = Settings(
            user_id=current_user.id,
            theme="light",
            language="en",
            timezone="UTC",
            date_format="MM/DD/YYYY",
            currency_format="USD"
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


@router.put("/", response_model=UserSettingsResponse)
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's settings."""
    settings = db.query(Settings).filter(Settings.user_id == current_user.id).first()
    
    if not settings:
        # Create new settings if they don't exist
        settings = Settings(user_id=current_user.id)
        db.add(settings)
    
    # Update fields
    update_data = settings_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    return settings


@router.get("/company", response_model=CompanyResponse)
async def get_company_settings(
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Get company settings (admin only)."""
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company


@router.put("/company", response_model=CompanyResponse)
async def update_company_settings(
    company_update: CompanyUpdate,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Update company settings (admin only)."""
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Update fields
    update_data = company_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    
    db.commit()
    db.refresh(company)
    
    return company


@router.post("/company/logo")
async def upload_company_logo(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Upload company logo (admin only)."""
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Validate file type
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".svg"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = Path("backend/uploads/logos")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / filename
    
    # Save file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Update company logo URL
    logo_url = f"/uploads/logos/{filename}"
    company.logo_url = logo_url
    db.commit()
    
    return {
        "message": "Logo uploaded successfully",
        "logo_url": logo_url
    }
