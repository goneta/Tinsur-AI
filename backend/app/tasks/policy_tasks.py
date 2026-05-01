"""
Background tasks for policy management.
"""
import logging
import random
from datetime import date, timedelta
from decimal import Decimal

from celery import shared_task
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.repositories.policy_repository import PolicyRepository
from app.repositories.quote_repository import QuoteRepository
from app.repositories.endorsement_repository import EndorsementRepository
from app.services.policy_service import PolicyService
from app.services.notification_service import NotificationService
from app.models.company import Company
from app.models.policy import Policy

logger = logging.getLogger(__name__)


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


@shared_task(name='app.tasks.policy_tasks.auto_renew_policies')
def auto_renew_policies():
    """
    Auto-renew policies marked with auto_renew=True that expired within the last 24 hours.

    For each eligible policy:
    1. Create a renewed policy record with a 1-year extension.
    2. Mark the original policy as 'renewed'.
    3. Send a renewal confirmation notification to the client.

    Returns a summary string with counts of renewed and skipped policies.
    """
    db: Session = SessionLocal()
    today = date.today()
    yesterday = today - timedelta(days=1)

    total_renewed = 0
    total_skipped = 0

    try:
        # Find all policies with auto_renew=True that just expired (yesterday or today)
        eligible = (
            db.query(Policy)
            .filter(
                Policy.auto_renew.is_(True),
                Policy.status == 'expired',
                Policy.end_date >= yesterday,
                Policy.end_date <= today,
            )
            .all()
        )

        for policy in eligible:
            try:
                # Build new policy number
                suffix = random.randint(1000, 9999)
                new_policy_number = f"{policy.policy_number}-R{suffix}"

                # New term: same duration as original
                original_duration = (policy.end_date - policy.start_date).days
                new_start = today
                new_end = today + timedelta(days=original_duration)

                # Create the renewed policy row
                renewed = Policy(
                    company_id=policy.company_id,
                    client_id=policy.client_id,
                    policy_type_id=policy.policy_type_id,
                    policy_number=new_policy_number,
                    status='active',
                    premium_amount=policy.premium_amount,
                    coverage_amount=policy.coverage_amount,
                    start_date=new_start,
                    end_date=new_end,
                    auto_renew=policy.auto_renew,
                    deductible=policy.deductible if hasattr(policy, 'deductible') else None,
                )
                db.add(renewed)

                # Mark the original as renewed
                policy.status = 'renewed'

                db.flush()  # get renewed.id without committing

                # Send notification if client has email
                client = getattr(policy, 'client', None)
                if client and getattr(client, 'email', None):
                    try:
                        notification_service = NotificationService(db)
                        notification_service.send_quote_notification(
                            company_id=policy.company_id,
                            client_id=client.id,
                            client_email=client.email,
                            quote_number=new_policy_number,
                            status='auto_renewed',
                            premium_amount=float(policy.premium_amount),
                            channels=['email'],
                        )
                    except Exception as notify_err:
                        logger.warning(
                            "Auto-renewal notification failed for policy %s: %s",
                            policy.policy_number,
                            notify_err,
                        )

                total_renewed += 1
                logger.info(
                    "Auto-renewed policy %s → %s (term: %s – %s)",
                    policy.policy_number,
                    new_policy_number,
                    new_start,
                    new_end,
                )

            except Exception as policy_err:
                logger.error(
                    "Failed to auto-renew policy %s: %s", policy.policy_number, policy_err
                )
                total_skipped += 1

        db.commit()
        summary = f"Auto-renewal complete: {total_renewed} renewed, {total_skipped} skipped"
        logger.info(summary)
        return summary

    except Exception as e:
        db.rollback()
        logger.error("auto_renew_policies task failed: %s", e)
        raise e
    finally:
        db.close()
