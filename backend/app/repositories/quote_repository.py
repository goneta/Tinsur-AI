"""
Repository for quote operations.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from datetime import datetime, date

from app.models.quote import Quote


class QuoteRepository:
    """Repository for quote data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, quote: Quote) -> Quote:
        """Create a new quote."""
        self.db.add(quote)
        self.db.commit()
        self.db.refresh(quote)
        return quote
    
    def get_by_id(self, quote_id: UUID) -> Optional[Quote]:
        """Get quote by ID."""
        return self.db.query(Quote).filter(Quote.id == quote_id).options(joinedload(Quote.client), joinedload(Quote.creator)).first()
    
    def get_by_number(self, quote_number: str) -> Optional[Quote]:
        """Get quote by quote number."""
        return self.db.query(Quote).filter(Quote.quote_number == quote_number).first()
    
    def get_by_company(
        self,
        company_id: UUID,
        client_id: Optional[UUID] = None,
        policy_type_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Quote], int]:
        """Get quotes by company with filters."""
        query = self.db.query(Quote).filter(Quote.company_id == company_id).options(joinedload(Quote.client), joinedload(Quote.creator))
        
        if client_id:
            query = query.filter(Quote.client_id == client_id)
        if policy_type_id:
            query = query.filter(Quote.policy_type_id == policy_type_id)
        if status:
            query = query.filter(Quote.status == status)
        
        total = query.count()
        quotes = query.order_by(Quote.created_at.desc()).offset(skip).limit(limit).all()
        
        return quotes, total
    
    def get_by_client(self, client_id: UUID, skip: int = 0, limit: int = 50) -> tuple[List[Quote], int]:
        """Get quotes by client."""
        query = self.db.query(Quote).filter(Quote.client_id == client_id)
        total = query.count()
        quotes = query.order_by(Quote.created_at.desc()).offset(skip).limit(limit).all()
        return quotes, total
    
    def get_by_status(self, company_id: UUID, status: str) -> List[Quote]:
        """Get quotes by status."""
        return self.db.query(Quote).filter(
            and_(
                Quote.company_id == company_id,
                Quote.status == status
            )
        ).all()
    
    def get_expired_quotes(self, company_id: UUID) -> List[Quote]:
        """Get expired quotes that need status update."""
        today = date.today()
        return self.db.query(Quote).filter(
            and_(
                Quote.company_id == company_id,
                Quote.valid_until < today,
                Quote.status.in_(['draft', 'sent'])
            )
        ).all()
    
    def update(self, quote: Quote) -> Quote:
        """Update a quote."""
        self.db.commit()
        self.db.refresh(quote)
        return quote
    
    def delete(self, quote_id: UUID) -> bool:
        """Delete a quote."""
        quote = self.get_by_id(quote_id)
        if quote:
            self.db.delete(quote)
            self.db.commit()
            return True
        return False
    
    def search(self, company_id: UUID, search_term: str, skip: int = 0, limit: int = 50) -> tuple[List[Quote], int]:
        """Search quotes by quote number or client info."""
        query = self.db.query(Quote).filter(
            and_(
                Quote.company_id == company_id,
                or_(
                    Quote.quote_number.ilike(f'%{search_term}%'),
                    Quote.notes.ilike(f'%{search_term}%')
                )
            )
        )
        total = query.count()
        quotes = query.order_by(Quote.created_at.desc()).offset(skip).limit(limit).all()
        return quotes, total
