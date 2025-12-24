"""
Repository for payment operations.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, date

from app.models.payment import Payment, PaymentTransaction


class PaymentRepository:
    """Repository for payment data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, payment: Payment) -> Payment:
        """Create a new payment."""
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def get_by_id(self, payment_id: UUID) -> Optional[Payment]:
        """Get payment by ID."""
        from sqlalchemy.orm import joinedload
        return self.db.query(Payment).options(
            joinedload(Payment.client),
            joinedload(Payment.policy),
            joinedload(Payment.creator)
        ).filter(Payment.id == payment_id).first()
    
    def get_by_number(self, payment_number: str) -> Optional[Payment]:
        """Get payment by payment number."""
        return self.db.query(Payment).filter(Payment.payment_number == payment_number).first()
    
    def get_by_policy(self, policy_id: UUID) -> List[Payment]:
        """Get all payments for a policy."""
        from sqlalchemy.orm import joinedload
        return self.db.query(Payment).options(
            joinedload(Payment.client),
            joinedload(Payment.policy),
            joinedload(Payment.creator)
        ).filter(Payment.policy_id == policy_id).order_by(Payment.created_at.desc()).all()
    
    def get_by_client(self, client_id: UUID, skip: int = 0, limit: int = 50) -> tuple[List[Payment], int]:
        """Get payments by client."""
        query = self.db.query(Payment).filter(Payment.client_id == client_id)
        total = query.count()
        payments = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
        return payments, total
    
    def get_by_company(
        self,
        company_id: UUID,
        status: Optional[str] = None,
        payment_method: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Payment], int]:
        """Get payments by company with filters."""
        from sqlalchemy.orm import joinedload
        query = self.db.query(Payment).filter(Payment.company_id == company_id)
        
        if status:
            query = query.filter(Payment.status == status)
        if payment_method:
            query = query.filter(Payment.payment_method == payment_method)
        
        total = query.count()
        payments = query.options(
            joinedload(Payment.client),
            joinedload(Payment.policy),
            joinedload(Payment.creator)
        ).order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
        
        return payments, total
    
    def get_failed_payments(self, company_id: UUID, retry_eligible: bool = True) -> List[Payment]:
        """Get failed payments for retry."""
        query = self.db.query(Payment).filter(
            and_(
                Payment.company_id == company_id,
                Payment.status == 'failed'
            )
        )
        return query.all()
    
    def update_status(self, payment_id: UUID, status: str, metadata: Optional[dict] = None) -> Optional[Payment]:
        """Update payment status."""
        payment = self.get_by_id(payment_id)
        if payment:
            payment.status = status
            if metadata:
                payment.metadata.update(metadata)
            if status == 'completed':
                payment.paid_at = datetime.utcnow()
            elif status == 'refunded':
                payment.refunded_at = datetime.utcnow()
            return self.update(payment)
        return None
    
    def update(self, payment: Payment) -> Payment:
        """Update a payment."""
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    # Payment Transaction methods
    def create_transaction(self, transaction: PaymentTransaction) -> PaymentTransaction:
        """Create a payment transaction."""
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def get_transaction_by_id(self, transaction_id: str) -> Optional[PaymentTransaction]:
        """Get transaction by gateway transaction ID."""
        return self.db.query(PaymentTransaction).filter(PaymentTransaction.transaction_id == transaction_id).first()
    
    def get_transactions_by_payment(self, payment_id: UUID) -> List[PaymentTransaction]:
        """Get all transactions for a payment."""
        return self.db.query(PaymentTransaction).filter(PaymentTransaction.payment_id == payment_id).order_by(PaymentTransaction.initiated_at.desc()).all()
    
    # Financial reconciliation queries
    def get_revenue_summary(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date
    ) -> dict:
        """Get revenue summary for a date range."""
        result = self.db.query(
            func.sum(Payment.amount).label('total_revenue'),
            func.count(Payment.id).label('total_payments')
        ).filter(
            and_(
                Payment.company_id == company_id,
                Payment.status == 'completed',
                func.date(Payment.paid_at) >= start_date,
                func.date(Payment.paid_at) <= end_date
            )
        ).first()
        
        return {
            'total_revenue': float(result.total_revenue or 0),
            'total_payments': result.total_payments or 0
        }
    
    def get_payment_breakdown(self, company_id: UUID, start_date: date, end_date: date) -> List[dict]:
        """Get payment breakdown by method."""
        results = self.db.query(
            Payment.payment_method,
            func.sum(Payment.amount).label('total'),
            func.count(Payment.id).label('count')
        ).filter(
            and_(
                Payment.company_id == company_id,
                Payment.status == 'completed',
                func.date(Payment.paid_at) >= start_date,
                func.date(Payment.paid_at) <= end_date
            )
        ).group_by(Payment.payment_method).all()
        
        return [
            {
                'method': r.payment_method,
                'total': float(r.total),
                'count': r.count
            }
            for r in results
        ]
