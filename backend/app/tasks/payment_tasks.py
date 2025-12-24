"""
Background tasks for payment management.
"""
from celery import shared_task
from sqlalchemy.orm import Session
from datetime import date

from app.core.database import SessionLocal
from app.repositories.premium_schedule_repository import PremiumScheduleRepository
from app.services.premium_service import PremiumService
from app.services.notification_service import NotificationService
from app.models.company import Company


@shared_task(name='app.tasks.payment_tasks.send_payment_reminders')
def send_payment_reminders():
    """Send payment reminders for upcoming payments."""
    db: Session = SessionLocal()
    
    try:
        companies = db.query(Company).all()
        
        total_reminders = 0
        for company in companies:
            schedule_repo = PremiumScheduleRepository(db)
            notification_service = NotificationService(db)
            
            # Get schedules due in next 7 days
            upcoming_schedules = schedule_repo.get_upcoming_due(company.id, days=7)
            
            for schedule in upcoming_schedules:
                # Get policy and client info
                policy = schedule.policy
                client = policy.client
                
                if client.email:
                    notification_service.send_payment_reminder(
                        company_id=company.id,
                        client_id=client.id,
                        client_email=client.email,
                        client_phone=client.phone,
                        policy_number=policy.policy_number,
                        amount=float(schedule.amount),
                        due_date=schedule.due_date.isoformat(),
                        channels=['email']
                    )
                    total_reminders += 1
                
                # Mark reminder as sent
                schedule.reminder_sent_at = date.today()
                schedule_repo.update(schedule)
        
        db.commit()
        return f"Sent {total_reminders} payment reminders"
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


@shared_task(name='app.tasks.payment_tasks.send_overdue_reminders')
def send_overdue_reminders():
    """Send reminders for overdue payments."""
    db: Session = SessionLocal()
    
    try:
        companies = db.query(Company).all()
        
        total_reminders = 0
        for company in companies:
            schedule_repo = PremiumScheduleRepository(db)
            premium_service = PremiumService(schedule_repo)
            notification_service = NotificationService(db)
            
            # Get overdue schedules
            overdue_schedules = premium_service.get_overdue_payments(company.id)
            
            for schedule in overdue_schedules:
                # Apply late fee if not already applied
                if not schedule.late_fee_applied:
                    premium_service.apply_late_fee(schedule.id)
                
                # Send overdue reminder
                policy = schedule.policy
                client = policy.client
                
                if client.email:
                    notification_service.send_payment_reminder(
                        company_id=company.id,
                        client_id=client.id,
                        client_email=client.email,
                        client_phone=client.phone,
                        policy_number=policy.policy_number,
                        amount=float(schedule.amount + schedule.late_fee),
                        due_date=schedule.due_date.isoformat(),
                        channels=['email', 'sms']
                    )
                    total_reminders += 1
                
                schedule.overdue_reminder_sent_at = date.today()
                schedule_repo.update(schedule)
        
        db.commit()
        return f"Sent {total_reminders} overdue reminders"
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


@shared_task(name='app.tasks.payment_tasks.process_failed_payment_retries')
def process_failed_payment_retries():
    """Retry failed payments."""
    # Implementation for retrying failed payments
    pass


@shared_task(name='app.tasks.payment_tasks.reconcile_payments')
def reconcile_payments():
    """Daily payment reconciliation."""
    # Implementation for payment reconciliation
    pass
