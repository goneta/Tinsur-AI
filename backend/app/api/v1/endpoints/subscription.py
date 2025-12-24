from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User
from app.models.company import Company
from app.models.system_settings import AiUsageLog
from app.services.ai_service import AiService
from app.services.payment_service import PaymentService
from app.repositories.payment_repository import PaymentRepository

router = APIRouter()

class AiUsageLogResponse(BaseModel):
    id: UUID
    company_id: UUID
    user_id: UUID
    agent_name: str
    action: str
    credits_consumed: float
    created_at: datetime

    class Config:
        from_attributes = True

class UsageStat(BaseModel):
    date: str
    credits: float
    count: int

class PlanUpdate(BaseModel):
    ai_plan: str # 'BASIC', 'BYOK', 'CREDIT'

class ApiKeyUpdate(BaseModel):
    api_key: str

class SuperAdminKeyUpdate(BaseModel):
    provider: str # 'google', 'openai', 'anthropic'
    api_key: str

class SubscriptionStatus(BaseModel):
    plan: str
    credits: float
    has_custom_key: bool
    company_id: str

class TopupRequest(BaseModel):
    amount: float
    payment_method: str # 'stripe', 'mobile_money'
    payment_gateway: Optional[str] = None # 'orange_money', 'mtn_money', 'wave'
    phone_number: Optional[str] = None # For mobile money
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None

class WebhookPayload(BaseModel):
    transaction_id: str
    status: str
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@router.get("/status", response_model=SubscriptionStatus)
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return SubscriptionStatus(
        plan=company.ai_plan or "CREDIT",
        credits=company.ai_credits_balance or 0.0,
        has_custom_key=bool(company.ai_api_key_encrypted),
        company_id=str(company.id)
    )

@router.post("/plan")
async def update_plan(
    update: PlanUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only company admin or super admin can change plans
    if current_user.role not in ["company_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to change subscription plan")
    
    if update.ai_plan not in ["BASIC", "BYOK", "CREDIT"]:
        raise HTTPException(status_code=400, detail="Invalid plan type")
    
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    company.ai_plan = update.ai_plan
    db.commit()
    return {"message": f"Plan updated to {update.ai_plan}"}

@router.post("/keys")
async def update_company_key(
    update: ApiKeyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["company_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to update keys")
    
    ai_service = AiService(db)
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    company.ai_api_key_encrypted = ai_service.encrypt_key(update.api_key)
    db.commit()
    return {"message": "API Key updated successfully"}

@router.post("/system/keys")
async def update_system_key(
    update: SuperAdminKeyUpdate,
    current_user: User = Depends(require_admin), # Super Admin only
    db: Session = Depends(get_db)
):
    # require_admin checks if role == 'super_admin'
    ai_service = AiService(db)
    ai_service.set_system_api_key(update.provider, update.api_key)
    return {"message": f"System {update.provider} key updated successfully"}

@router.get("/system/usage", response_model=List[AiUsageLogResponse])
async def get_system_usage(
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get aggregate AI usage logs for Super Admin."""
    logs = db.query(AiUsageLog).order_by(AiUsageLog.created_at.desc()).limit(limit).all()
    return logs

@router.get("/usage/stats", response_model=List[UsageStat])
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from sqlalchemy import func
    from datetime import timedelta
    
    if not current_user.company_id:
        return []

    # Last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Aggregate by date
    # Using func.date for grouping - works on both SQLite and Postgres
    stats = db.query(
        func.date(AiUsageLog.created_at).label('date'),
        func.sum(AiUsageLog.credits_consumed).label('credits'),
        func.count(AiUsageLog.id).label('count')
    ).filter(
        AiUsageLog.company_id == current_user.company_id,
        AiUsageLog.created_at >= thirty_days_ago
    ).group_by(
        func.date(AiUsageLog.created_at)
    ).order_by(
        func.date(AiUsageLog.created_at).asc()
    ).all()
    
    return [UsageStat(date=str(s.date), credits=float(s.credits or 0), count=int(s.count or 0)) for s in stats]

@router.post("/topup")
async def initiate_topup(
    request: TopupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate a credit top-up."""
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="User must belong to a company")
        
    payment_repo = PaymentRepository(db)
    payment_service = PaymentService(db, payment_repo)
    
    # Create payment record
    payment = payment_service.create_payment(
        company_id=current_user.company_id,
        policy_id=None, # Not linked to a policy
        client_id=None, # Admin is the payer
        amount=request.amount,
        payment_method=request.payment_method,
        payment_gateway=request.payment_gateway,
        metadata={
            "type": "ai_credits",
            "initiated_by": str(current_user.id)
        }
    )
    
    # Process payment (this might return a checkout URL or instructions)
    details = {
        "phone_number": request.phone_number,
        "success_url": request.success_url,
        "cancel_url": request.cancel_url
    }
    
    result = payment_service.process_payment(payment.id, details)
    
    # Find the initiated transaction to get redirection info
    transaction = db.query(PaymentRepository.model_transaction).filter(
        PaymentRepository.model_transaction.payment_id == payment.id
    ).order_by(PaymentRepository.model_transaction.initiated_at.desc()).first()
    
    return {
        "payment_id": str(payment.id),
        "status": payment.status,
        "gateway_response": transaction.gateway_response if transaction else {}
    }

@router.post("/webhook/{gateway}")
async def payment_webhook(
    gateway: str,
    payload: WebhookPayload,
    db: Session = Depends(get_db)
):
    """Handle payment gateway webhooks."""
    payment_repo = PaymentRepository(db)
    payment_service = PaymentService(db, payment_repo)
    
    payment = payment_service.handle_webhook(gateway, payload.model_dump())
    
    if not payment:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    return {"message": "Webhook processed", "status": payment.status}
