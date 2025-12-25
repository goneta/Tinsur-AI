"""
Admin/stats endpoints for dashboard.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User
from app.models.client import Client
from app.models.policy import Policy
from app.models.quote import Quote
from app.services.security_service import SecurityService
from datetime import date, timedelta, datetime

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics."""
    company_id = current_user.company_id
    
    # Count clients by status
    total_clients = db.query(Client).filter(
        Client.company_id == company_id
    ).count()
    
    active_clients = db.query(Client).filter(
        Client.company_id == company_id,
        Client.status == "active"
    ).count()
    
    # Count users by role
    total_users = db.query(User).filter(
        User.company_id == company_id
    ).count()
    
    agents_count = db.query(User).filter(
        User.company_id == company_id,
        User.role == "agent"
    ).count()
    
    # Risk profile distribution
    risk_distribution = db.query(
        Client.risk_profile,
        func.count(Client.id).label('count')
    ).filter(
        Client.company_id == company_id
    ).group_by(Client.risk_profile).all()
    
    risk_dist_dict = {profile: count for profile, count in risk_distribution}
    
    # Count active policies
    active_policies = db.query(Policy).filter(
        Policy.company_id == company_id,
        Policy.status == "active"
    ).count()

    # Count pending quotes
    pending_quotes = db.query(Quote).filter(
        Quote.company_id == company_id,
        Quote.status.in_(["draft", "sent"])
    ).count()

    # --- GROWTH CALCULATIONS ---
    # Current month start and end
    today = date.today()
    start_cur = date(today.year, today.month, 1)
    
    # Last month start and end
    last_month_date = start_cur - timedelta(days=1)
    start_prev = date(last_month_date.year, last_month_date.month, 1)
    end_prev = start_cur - timedelta(days=1)

    def calculate_growth(current, previous):
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 1)

    # Client Growth
    cur_clients = db.query(Client).filter(Client.company_id == company_id, Client.created_at >= start_cur).count()
    prev_clients = db.query(Client).filter(Client.company_id == company_id, Client.created_at >= start_prev, Client.created_at <= end_prev).count()
    clients_growth = calculate_growth(cur_clients, prev_clients)

    # Policy Growth
    cur_policies = db.query(Policy).filter(Policy.company_id == company_id, Policy.created_at >= start_cur).count()
    prev_policies = db.query(Policy).filter(Policy.company_id == company_id, Policy.created_at >= start_prev, Policy.created_at <= end_prev).count()
    policies_growth = calculate_growth(cur_policies, prev_policies)

    # Quote Growth
    cur_quotes = db.query(Quote).filter(Quote.company_id == company_id, Quote.created_at >= start_cur).count()
    prev_quotes = db.query(Quote).filter(Quote.company_id == company_id, Quote.created_at >= start_prev, Quote.created_at <= end_prev).count()
    quotes_growth = calculate_growth(cur_quotes, prev_quotes)

    # Revenue Growth
    monthly_revenue = db.query(func.sum(Policy.premium_amount)).filter(
        Policy.company_id == company_id,
        Policy.created_at >= start_cur
    ).scalar() or 0
    
    prev_revenue = db.query(func.sum(Policy.premium_amount)).filter(
        Policy.company_id == company_id,
        Policy.created_at >= start_prev,
        Policy.created_at <= end_prev
    ).scalar() or 0
    revenue_growth = calculate_growth(float(monthly_revenue), float(prev_revenue))

    return {
        "clients": {
            "total": total_clients,
            "active": active_clients,
            "inactive": total_clients - active_clients,
            "by_risk_profile": risk_dist_dict,
            "growth": clients_growth
        },
        "users": {
            "total": total_users,
            "agents": agents_count
        },
        "policies": {
            "active": active_policies,
            "growth": policies_growth
        },
        "quotes": {
            "pending": pending_quotes,
            "growth": quotes_growth
        },
        "revenue": {
            "monthly": float(monthly_revenue),
            "growth": revenue_growth
        }
    }


@router.get("/recent-activity")
async def get_recent_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent activity (unified list of clients, policies, results)."""
    company_id = current_user.company_id
    
    activities = []
    
    # Recent Clients
    recent_clients = db.query(Client).filter(
        Client.company_id == company_id
    ).order_by(Client.created_at.desc()).limit(5).all()
    
    for c in recent_clients:
        activities.append({
            "type": "client",
            "title": "New Client Registered",
            "description": f"{c.display_name} ({c.client_type})",
            "amount": None,
            "created_at": c.created_at.isoformat()
        })
        
    # Recent Policies
    recent_policies = db.query(Policy).options(joinedload(Policy.client)).filter(
        Policy.company_id == company_id
    ).order_by(Policy.created_at.desc()).limit(5).all()
    
    for p in recent_policies:
        activities.append({
            "type": "policy",
            "title": "New Policy Created",
            "description": f"{p.policy_number} for {p.client.display_name if p.client else 'Unknown'}",
            "amount": f"+{float(p.premium_amount):,} XOF",
            "created_at": p.created_at.isoformat()
        })
        
    # Recent Quotes
    recent_quotes = db.query(Quote).options(joinedload(Quote.client)).filter(
        Quote.company_id == company_id
    ).order_by(Quote.created_at.desc()).limit(5).all()
    
    for q in recent_quotes:
        activities.append({
            "type": "quote",
            "title": f"Quote {q.status.title()}",
            "description": f"{q.quote_number} for {q.client.display_name if q.client else 'Unknown'}",
            "amount": "Processing" if q.status == 'draft' else None,
            "created_at": q.created_at.isoformat()
        })
        
    # Sort and Limit
    activities.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "activities": activities[:10]
    }
from app.models.rbac import Role, Permission
from pydantic import BaseModel
from typing import List, Optional

class PermissionBase(BaseModel):
    id: str
    scope: str
    action: str
    description: Optional[str] = None
    key: str

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[PermissionBase] = []

    class Config:
        from_attributes = True

class PermissionCreate(BaseModel):
    scope: str
    action: str
    description: Optional[str] = None

class AssignPermissionsRequest(BaseModel):
    permission_ids: List[str]

@router.get("/roles", response_model=List[RoleBase])
def list_roles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    security = SecurityService(db)
    security.enforce_permission(current_user, "admin", "read")
    return db.query(Role).options(joinedload(Role.permissions)).all()

@router.get("/permissions", response_model=List[PermissionBase])
def list_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    security = SecurityService(db)
    security.enforce_permission(current_user, "admin", "read")
    return db.query(Permission).all()

@router.post("/roles/{role_id}/permissions")
def assign_permissions_to_role(
    role_id: str,
    request: AssignPermissionsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    security = SecurityService(db)
    security.enforce_permission(current_user, "admin", "write")
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    role.permissions = []
    for pid in request.permission_ids:
        perm = db.query(Permission).filter(Permission.id == pid).first()
        if perm:
            role.permissions.append(perm)
            
    db.commit()
    db.refresh(role)
    return {"status": "success", "role": role.name, "permission_count": len(role.permissions)}

@router.post("/permissions", response_model=PermissionBase)
def create_permission(
    permission_in: PermissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    security = SecurityService(db)
    security.enforce_permission(current_user, "admin", "write")
    
    existing = db.query(Permission).filter(
        Permission.scope == permission_in.scope,
        Permission.action == permission_in.action
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Permission already exists")
    
    permission = Permission(
        scope=permission_in.scope,
        action=permission_in.action,
        description=permission_in.description
    )
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission
