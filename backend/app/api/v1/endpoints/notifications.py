"""
Notification endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.notification import Notification
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent notifications for the current user."""
    query = db.query(Notification).filter(
        Notification.company_id == current_user.company_id,
        Notification.user_id == current_user.id
    )
    
    if unread_only:
        query = query.filter(Notification.status != 'read')
        
    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": str(n.id),
            "type": n.notification_type,
            "channel": n.channel,
            "subject": n.subject,
            "content": n.content,
            "status": n.status,
            "created_at": n.created_at.isoformat(),
            "metadata": n.notification_metadata or {}
        }
        for n in notifications
    ]

@router.patch("/{notification_id}/read", status_code=status.HTTP_200_OK)
async def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    notification.status = 'read'
    import datetime
    notification.read_at = datetime.datetime.utcnow()
    db.commit()
    
    return {"message": "Marked as read"}
