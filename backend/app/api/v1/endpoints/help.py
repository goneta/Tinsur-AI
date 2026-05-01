"""Help and Onboarding Guide API Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from uuid import uuid4
from datetime import datetime
import os
import re

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.help_guide import (
    HelpGuide, GuideCompletion, GuideAccess, OnboardingStatus,
    GuideType, GuideSection
)

router = APIRouter()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_guide_from_file(guide_type: GuideType) -> dict:
    """Load guide content from markdown file"""
    file_map = {
        GuideType.CLIENT: "ONBOARDING-CLIENT.md",
        GuideType.ADMIN: "ONBOARDING-ADMIN.md",
        GuideType.INSURANCE_COMPANY: "ONBOARDING-INSURANCE-COMPANY.md"
    }
    
    file_name = file_map.get(guide_type)
    if not file_name:
        raise ValueError(f"Unknown guide type: {guide_type}")
    
    # Try multiple possible paths
    possible_paths = [
        f"C:\\THUNDERFAM APPS\\tinsur-ai\\docs\\{file_name}",
        f"../../../docs/{file_name}",
        f"docs/{file_name}",
        f"backend/../../docs/{file_name}",
    ]
    
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break
    
    if not file_path:
        raise FileNotFoundError(f"Guide file not found for type: {guide_type}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return {
        "title": f"Tinsur-AI {guide_type.value.title()} Onboarding Guide",
        "content": content,
        "guide_type": guide_type.value
    }


def parse_guide_sections(content: str) -> List[dict]:
    """Parse markdown content into sections"""
    sections = []
    current_section = None
    current_content = []
    
    for line in content.split('\n'):
        if line.startswith('## '):
            if current_section:
                sections.append({
                    "title": current_section,
                    "content": '\n'.join(current_content).strip()
                })
            current_section = line[3:].strip()
            current_content = []
        elif current_section is not None:
            current_content.append(line)
    
    if current_section:
        sections.append({
            "title": current_section,
            "content": '\n'.join(current_content).strip()
        })
    
    return sections


# ============================================================================
# PUBLIC ENDPOINTS (No Auth Required)
# ============================================================================

@router.get("/guides", response_model=List[dict])
async def get_guides(
    guide_type: Optional[GuideType] = None,
    section: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all available help guides - Public access"""
    query = db.query(HelpGuide).filter(HelpGuide.is_active == True)
    
    if guide_type:
        query = query.filter(HelpGuide.guide_type == guide_type)
    
    if section:
        query = query.filter(HelpGuide.section == section)
    
    guides = query.order_by(HelpGuide.display_order).all()
    
    return [
        {
            "id": g.id,
            "title": g.title,
            "description": g.description,
            "guide_type": g.guide_type.value,
            "section": g.section.value if g.section else None,
            "estimated_read_time": g.estimated_read_time,
            "tags": g.tags.split(",") if g.tags else [],
            "created_at": g.created_at.isoformat()
        }
        for g in guides
    ]


@router.get("/guides/{guide_id}", response_model=dict)
async def get_guide(guide_id: str, db: Session = Depends(get_db)):
    """Get a specific guide by ID - Public access"""
    guide = db.query(HelpGuide).filter(
        and_(HelpGuide.id == guide_id, HelpGuide.is_active == True)
    ).first()
    
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    
    return {
        "id": guide.id,
        "title": guide.title,
        "description": guide.description,
        "content": guide.content,
        "guide_type": guide.guide_type.value,
        "section": guide.section.value if guide.section else None,
        "estimated_read_time": guide.estimated_read_time,
        "tags": guide.tags.split(",") if guide.tags else [],
        "created_at": guide.created_at.isoformat(),
        "updated_at": guide.updated_at.isoformat()
    }


@router.get("/search", response_model=List[dict])
async def search_guides(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """Search guides by title, description, content, or tags"""
    search_term = f"%{q}%"
    
    guides = db.query(HelpGuide).filter(
        and_(
            HelpGuide.is_active == True,
            or_(
                HelpGuide.title.ilike(search_term),
                HelpGuide.description.ilike(search_term),
                HelpGuide.content.ilike(search_term),
                HelpGuide.tags.ilike(search_term)
            )
        )
    ).order_by(HelpGuide.display_order).all()
    
    return [
        {
            "id": g.id,
            "title": g.title,
            "description": g.description,
            "guide_type": g.guide_type.value,
            "section": g.section.value if g.section else None,
            "estimated_read_time": g.estimated_read_time,
            "tags": g.tags.split(",") if g.tags else []
        }
        for g in guides
    ]


# ============================================================================
# AUTHENTICATED ENDPOINTS
# ============================================================================

@router.post("/guides/{guide_id}/mark-complete")
async def mark_guide_complete(
    guide_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a guide as completed by user"""
    # Verify guide exists
    guide = db.query(HelpGuide).filter(HelpGuide.id == guide_id).first()
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    
    # Check if already completed
    existing = db.query(GuideCompletion).filter(
        and_(
            GuideCompletion.user_id == current_user.id,
            GuideCompletion.guide_id == guide_id
        )
    ).first()
    
    if existing:
        return {"message": "Guide already marked as completed"}
    
    # Create completion record
    completion = GuideCompletion(
        id=str(uuid4()),
        user_id=current_user.id,
        guide_id=guide_id,
        completed_at=datetime.utcnow()
    )
    
    db.add(completion)
    db.commit()
    
    return {"message": "Guide marked as completed", "completed_at": completion.completed_at.isoformat()}


@router.get("/guides/{guide_id}/access")
async def track_guide_access(
    guide_id: str,
    section: Optional[str] = None,
    time_spent: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track guide access for analytics"""
    # Verify guide exists
    guide = db.query(HelpGuide).filter(HelpGuide.id == guide_id).first()
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    
    # Create access record
    access = GuideAccess(
        id=str(uuid4()),
        user_id=current_user.id,
        guide_id=guide_id,
        section_accessed=section,
        time_spent_seconds=time_spent
    )
    
    db.add(access)
    db.commit()
    
    return {"message": "Access recorded"}


@router.get("/completion-status")
async def get_completion_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's guide completion status"""
    completions = db.query(GuideCompletion).filter(
        GuideCompletion.user_id == current_user.id
    ).all()
    
    completed_guide_ids = {c.guide_id for c in completions}
    
    return {
        "user_id": current_user.id,
        "completed_guides": list(completed_guide_ids),
        "total_completed": len(completed_guide_ids),
        "completion_records": [
            {
                "guide_id": c.guide_id,
                "completed_at": c.completed_at.isoformat()
            }
            for c in completions
        ]
    }


# ============================================================================
# ONBOARDING ENDPOINTS
# ============================================================================

@router.get("/onboarding/status")
async def get_onboarding_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's onboarding status"""
    status = db.query(OnboardingStatus).filter(
        OnboardingStatus.user_id == current_user.id
    ).first()
    
    if not status:
        # Create new onboarding status if doesn't exist
        status = OnboardingStatus(
            id=str(uuid4()),
            user_id=current_user.id,
            current_step=0,
            completed=False,
            skipped=False
        )
        db.add(status)
        db.commit()
    
    return {
        "user_id": current_user.id,
        "current_step": status.current_step,
        "completed": status.completed,
        "skipped": status.skipped,
        "last_accessed_at": status.last_accessed_at.isoformat() if status.last_accessed_at else None,
        "created_at": status.created_at.isoformat(),
        "updated_at": status.updated_at.isoformat()
    }


@router.post("/onboarding/next-step")
async def update_onboarding_step(
    step: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's onboarding step"""
    status = db.query(OnboardingStatus).filter(
        OnboardingStatus.user_id == current_user.id
    ).first()
    
    if not status:
        status = OnboardingStatus(
            id=str(uuid4()),
            user_id=current_user.id,
            current_step=step
        )
        db.add(status)
    else:
        status.current_step = step
        status.last_accessed_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "user_id": current_user.id,
        "current_step": status.current_step,
        "updated_at": status.updated_at.isoformat()
    }


@router.post("/onboarding/complete")
async def complete_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark onboarding as complete"""
    status = db.query(OnboardingStatus).filter(
        OnboardingStatus.user_id == current_user.id
    ).first()
    
    if not status:
        status = OnboardingStatus(
            id=str(uuid4()),
            user_id=current_user.id,
            completed=True,
            completed_at=datetime.utcnow()
        )
        db.add(status)
    else:
        status.completed = True
        status.completed_at = datetime.utcnow()
        status.last_accessed_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "user_id": current_user.id,
        "completed": True,
        "completed_at": status.completed_at.isoformat()
    }


@router.post("/onboarding/skip")
async def skip_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Skip onboarding with option to complete later"""
    status = db.query(OnboardingStatus).filter(
        OnboardingStatus.user_id == current_user.id
    ).first()
    
    if not status:
        status = OnboardingStatus(
            id=str(uuid4()),
            user_id=current_user.id,
            skipped=True
        )
        db.add(status)
    else:
        status.skipped = True
        status.last_accessed_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "user_id": current_user.id,
        "skipped": True,
        "message": "Onboarding skipped. You can complete it later from Settings."
    }


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@router.post("/admin/guides/init-from-files")
async def initialize_guides_from_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initialize guides from markdown files (Admin only)"""
    # Check if user is admin
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    guide_types = [GuideType.CLIENT, GuideType.ADMIN, GuideType.INSURANCE_COMPANY]
    created_guides = []
    
    for guide_type in guide_types:
        try:
            guide_data = load_guide_from_file(guide_type)
            
            # Check if already exists
            existing = db.query(HelpGuide).filter(
                HelpGuide.guide_type == guide_type
            ).first()
            
            if existing:
                # Update existing
                existing.title = guide_data["title"]
                existing.content = guide_data["content"]
                existing.updated_at = datetime.utcnow()
                db.commit()
                created_guides.append({
                    "guide_type": guide_type.value,
                    "status": "updated"
                })
            else:
                # Create new
                guide = HelpGuide(
                    id=str(uuid4()),
                    title=guide_data["title"],
                    description=f"Comprehensive onboarding guide for {guide_type.value}",
                    content=guide_data["content"],
                    guide_type=guide_type,
                    display_order=len(created_guides),
                    is_active=True
                )
                db.add(guide)
                db.commit()
                created_guides.append({
                    "guide_type": guide_type.value,
                    "status": "created",
                    "id": guide.id
                })
        except Exception as e:
            created_guides.append({
                "guide_type": guide_type.value,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "message": "Guide initialization completed",
        "results": created_guides
    }


@router.get("/admin/analytics")
async def get_help_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics on guide usage (Admin only)"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    total_accesses = db.query(GuideAccess).count()
    total_completions = db.query(GuideCompletion).count()
    total_users_accessing = db.query(GuideAccess.user_id).distinct().count()
    
    # Most accessed guides
    from sqlalchemy import func
    most_accessed = db.query(
        GuideAccess.guide_id,
        func.count(GuideAccess.id).label("access_count")
    ).group_by(GuideAccess.guide_id).order_by(func.count(GuideAccess.id).desc()).limit(10).all()
    
    return {
        "total_accesses": total_accesses,
        "total_completions": total_completions,
        "unique_users": total_users_accessing,
        "most_accessed_guides": [
            {"guide_id": ma[0], "access_count": ma[1]}
            for ma in most_accessed
        ]
    }
