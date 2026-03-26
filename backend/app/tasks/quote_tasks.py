"""
Background tasks for quote management.
"""
from celery import shared_task
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.repositories.quote_repository import QuoteRepository
from app.services.quote_service import QuoteService
from app.models.company import Company


@shared_task(name='app.tasks.quote_tasks.check_expired_quotes')
def check_expired_quotes():
    """Check and mark expired quotes for all companies."""
    db: Session = SessionLocal()
    
    try:
        # Get all companies
        companies = db.query(Company).all()
        
        total_expired = 0
        for company in companies:
            quote_repo = QuoteRepository(db)
            quote_service = QuoteService(quote_repo)
            
            expired_count = quote_service.check_and_expire_quotes(company.id)
            total_expired += expired_count
        
        db.commit()
        return f"Marked {total_expired} quotes as expired"
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


@shared_task(name='app.tasks.quote_tasks.send_quote_followup')
def send_quote_followup():
    """Send follow-up reminders for quotes sent but not accepted."""
    db: Session = SessionLocal()
    
    try:
        # Implementation for quote follow-up
        # This would query quotes in 'sent' status for more than X days
        # and send reminder notifications
        pass
        
    finally:
        db.close()
