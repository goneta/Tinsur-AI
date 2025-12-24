"""
Background tasks for policy management.
"""
from celery import shared_task
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.repositories.policy_repository import PolicyRepository
from app.repositories.quote_repository import QuoteRepository
from app.repositories.endorsement_repository import EndorsementRepository
from app.services.policy_service import PolicyService
from app.services.notification_service import NotificationService
from app.models.company import Company


@shared_task(name='app.tasks.policy_tasks.check_policy_renewals')
def check_policy_renewals():
    """Check for policies nearing renewal and send reminders."""
    db: Session = SessionLocal()
    
    try:
        companies = db.query(Company).all()
        
        total_reminders = 0
        for company in companies:
            policy_repo = PolicyRepository(db)
            quote_repo = QuoteRepository(db)
            endorsement_repo = EndorsementRepository(db)
            policy_service = PolicyService(policy_repo, quote_repo, endorsement_repo)
            notification_service = NotificationService(db)
            
            # Get policies expiring in 30 days
            expiring_policies = policy_service.get_policies_for_renewal(company.id, days=30)
            
            for policy in expiring_policies:
                client = policy.client
                
                if client.email:
                    notification_service.send_policy_renewal_reminder(
                        company_id=company.id,
                        client_id=client.id,
                        client_email=client.email,
                        policy_number=policy.policy_number,
                        expiry_date=policy.end_date.isoformat(),
                        days_until_expiry=policy.days_until_expiry
                    )
                    total_reminders += 1
        
        db.commit()
        return f"Sent {total_reminders} renewal reminders"
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


@shared_task(name='app.tasks.policy_tasks.send_renewal_reminders')
def send_renewal_reminders():
    """Send renewal reminders (alias for check_policy_renewals)."""
    return check_policy_renewals()


@shared_task(name='app.tasks.policy_tasks.auto_lapse_policies')
def auto_lapse_policies():
    """Automatically lapse policies with unpaid premiums past grace period."""
    db: Session = SessionLocal()
    
    try:
        companies = db.query(Company).all()
        
        total_lapsed = 0
        for company in companies:
            policy_repo = PolicyRepository(db)
            quote_repo = QuoteRepository(db)
            endorsement_repo = EndorsementRepository(db)
            policy_service = PolicyService(policy_repo, quote_repo, endorsement_repo)
            
            # Mark expired policies
            lapsed_count = policy_service.check_and_expire_policies(company.id)
            total_lapsed += lapsed_count
        
        db.commit()
        return f"Lapsed {total_lapsed} policies"
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
