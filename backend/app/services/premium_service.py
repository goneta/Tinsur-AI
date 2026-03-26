"""
Premium schedule service for business logic operations.
"""
from typing import List
from uuid import UUID
from decimal import Decimal
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from app.models.premium_schedule import PremiumSchedule
from app.repositories.premium_schedule_repository import PremiumScheduleRepository


class PremiumService:
    """Service for premium schedule management."""
    
    def __init__(self, schedule_repo: PremiumScheduleRepository):
        self.schedule_repo = schedule_repo
    
    def generate_payment_schedule(
        self,
        company_id: UUID,
        policy_id: UUID,
        total_premium: Decimal,
        frequency: str,
        start_date: date,
        duration_months: int = 12,
        grace_period_days: int = 15
    ) -> List[PremiumSchedule]:
        """Generate payment schedule based on frequency."""
        schedules = []
        
        # Determine installment count and amount
        installment_config = {
            'monthly': {'count': duration_months, 'months_between': 1},
            'quarterly': {'count': duration_months // 3, 'months_between': 3},
            'semi-annual': {'count': duration_months // 6, 'months_between': 6},
            'annual': {'count': 1, 'months_between': 12}
        }
        
        config = installment_config.get(frequency, installment_config['annual'])
        installment_count = config['count']
        months_between = config['months_between']
        
        installment_amount = total_premium / Decimal(installment_count)
        
        # Generate schedules
        for i in range(installment_count):
            due_date = start_date + relativedelta(months=i * months_between)
            grace_period_ends = due_date + timedelta(days=grace_period_days)
            
            schedule = PremiumSchedule(
                company_id=company_id,
                policy_id=policy_id,
                installment_number=f"{i + 1} of {installment_count}",
                due_date=due_date,
                amount=installment_amount,
                status='pending',
                grace_period_days=Decimal(grace_period_days),
                grace_period_ends=grace_period_ends
            )
            schedules.append(schedule)
        
        return self.schedule_repo.create_bulk(schedules)
    
    def mark_schedule_as_paid(
        self,
        schedule_id: UUID,
        payment_id: UUID,
        amount: Decimal
    ) -> PremiumSchedule:
        """Mark a payment schedule as paid."""
        return self.schedule_repo.mark_as_paid(schedule_id, payment_id, amount)
    
    def apply_late_fee(
        self,
        schedule_id: UUID,
        late_fee_percent: Decimal = Decimal('5')
    ) -> PremiumSchedule:
        """Apply late fee to overdue schedule."""
        schedule = self.schedule_repo.get_by_id(schedule_id)
        
        if schedule and schedule.is_overdue and not schedule.late_fee_applied:
            late_fee = schedule.amount * (late_fee_percent / 100)
            schedule.late_fee = late_fee
            schedule.late_fee_applied = True
            schedule.status = 'overdue'
            return self.schedule_repo.update(schedule)
        
        return schedule
    
    def get_upcoming_payments(self, company_id: UUID, days: int = 7) -> List[PremiumSchedule]:
        """Get payment schedules due in the next N days."""
        return self.schedule_repo.get_upcoming_due(company_id, days)
    
    def get_overdue_payments(self, company_id: UUID) -> List[PremiumSchedule]:
        """Get all overdue payment schedules."""
        return self.schedule_repo.get_overdue(company_id)
