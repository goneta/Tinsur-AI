"""
Repository for premium schedule operations.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.models.premium_schedule import PremiumSchedule


class PremiumScheduleRepository:
    """Repository for premium schedule data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, schedule: PremiumSchedule) -> PremiumSchedule:
        """Create a new premium schedule."""
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule
    
    def create_bulk(self, schedules: List[PremiumSchedule]) -> List[PremiumSchedule]:
        """Create multiple premium schedules."""
        self.db.add_all(schedules)
        self.db.commit()
        for schedule in schedules:
            self.db.refresh(schedule)
        return schedules
    
    def get_by_id(self, schedule_id: UUID) -> Optional[PremiumSchedule]:
        """Get schedule by ID."""
        return self.db.query(PremiumSchedule).filter(PremiumSchedule.id == schedule_id).first()
    
    def get_by_policy(self, policy_id: UUID) -> List[PremiumSchedule]:
        """Get all schedules for a policy."""
        return self.db.query(PremiumSchedule).filter(
            PremiumSchedule.policy_id == policy_id
        ).order_by(PremiumSchedule.due_date).all()
    
    def get_pending_by_policy(self, policy_id: UUID) -> List[PremiumSchedule]:
        """Get pending schedules for a policy."""
        return self.db.query(PremiumSchedule).filter(
            and_(
                PremiumSchedule.policy_id == policy_id,
                PremiumSchedule.status == 'pending'
            )
        ).order_by(PremiumSchedule.due_date).all()
    
    def get_upcoming_due(self, company_id: UUID, days_ahead: int = 7) -> List[PremiumSchedule]:
        """Get schedules due within specified days."""
        today = date.today()
        target_date = today + timedelta(days=days_ahead)
        return self.db.query(PremiumSchedule).filter(
            and_(
                PremiumSchedule.company_id == company_id,
                PremiumSchedule.status == 'pending',
                PremiumSchedule.due_date >= today,
                PremiumSchedule.due_date <= target_date,
                PremiumSchedule.reminder_sent_at.is_(None)
            )
        ).all()
    
    def get_overdue(self, company_id: UUID) -> List[PremiumSchedule]:
        """Get overdue schedules."""
        today = date.today()
        return self.db.query(PremiumSchedule).filter(
            and_(
                PremiumSchedule.company_id == company_id,
                PremiumSchedule.status.in_(['pending', 'overdue']),
                PremiumSchedule.grace_period_ends < today
            )
        ).all()
    
    def update(self, schedule: PremiumSchedule) -> PremiumSchedule:
        """Update a schedule."""
        self.db.commit()
        self.db.refresh(schedule)
        return schedule
    
    def mark_as_paid(self, schedule_id: UUID, payment_id: UUID, amount: Decimal) -> Optional[PremiumSchedule]:
        """Mark a schedule as paid."""
        schedule = self.get_by_id(schedule_id)
        if schedule:
            schedule.status = 'paid'
            schedule.payment_id = payment_id
            schedule.paid_at = datetime.utcnow()
            schedule.paid_amount = amount
            return self.update(schedule)
        return None
    
    def get_outstanding_by_client(self, client_id: UUID) -> tuple[List[PremiumSchedule], Decimal]:
        """Get outstanding schedules for a client with total amount."""
        from app.models.policy import Policy
        
        schedules = self.db.query(PremiumSchedule).join(
            Policy, PremiumSchedule.policy_id == Policy.id
        ).filter(
            and_(
                Policy.client_id == client_id,
                PremiumSchedule.status.in_(['pending', 'overdue'])
            )
        ).order_by(PremiumSchedule.due_date).all()
        
        total_outstanding = sum(s.amount + s.late_fee for s in schedules)
        return schedules, Decimal(str(total_outstanding))
    
    def get_policy_summary(self, policy_id: UUID) -> dict:
        """Get payment schedule summary for a policy."""
        result = self.db.query(
            func.sum(PremiumSchedule.amount).label('total_amount'),
            func.sum(PremiumSchedule.paid_amount).label('paid_amount'),
            func.count(PremiumSchedule.id).label('total_installments')
        ).filter(PremiumSchedule.policy_id == policy_id).first()
        
        paid = float(result.paid_amount or 0)
        total = float(result.total_amount or 0)
        
        return {
            'total_amount': total,
            'paid_amount': paid,
            'outstanding_amount': total - paid,
            'total_installments': result.total_installments or 0
        }
