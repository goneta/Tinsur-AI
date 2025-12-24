"""
Loyalty Service for point management.
"""
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.loyalty import LoyaltyPoint
from app.models.client import Client

class LoyaltyService:
    """Service for handling loyalty points and tiers."""
    
    TIER_THRESHOLDS = {
        'platinum': 10000,
        'gold': 5000,
        'silver': 1000,
        'bronze': 0
    }
    
    def __init__(self, db: Session):
        self.db = db
        
    def get_or_create_loyalty(self, client_id: UUID) -> LoyaltyPoint:
        """Get or create loyalty record for a client."""
        loyalty = self.db.query(LoyaltyPoint).filter(LoyaltyPoint.client_id == client_id).first()
        if not loyalty:
            loyalty = LoyaltyPoint(client_id=client_id, points_balance=0, tier='bronze')
            self.db.add(loyalty)
            self.db.commit()
            self.db.refresh(loyalty)
        return loyalty
        
    def award_points(self, client_id: UUID, amount: Decimal, reason: str) -> LoyaltyPoint:
        """
        Award points based on payment amount.
        Rule: 1 point per 1000 XOF paid.
        """
        loyalty = self.get_or_create_loyalty(client_id)
        
        points_to_add = int(amount / 1000)
        if points_to_add <= 0:
            return loyalty
            
        loyalty.points_earned += points_to_add
        loyalty.points_balance += points_to_add
        
        # Check for tier progression
        self._update_tier(loyalty)
        
        self.db.commit()
        self.db.refresh(loyalty)
        return loyalty
        
    def redeem_points(self, client_id: UUID, points: int) -> Decimal:
        """
        Redeem points for currency.
        Rule: 100 points = 1000 XOF discount.
        """
        loyalty = self.get_or_create_loyalty(client_id)
        
        if points > loyalty.points_balance:
            raise ValueError("Insufficient points balance")
            
        discount_amount = Decimal(str(points / 100)) * Decimal('1000')
        
        loyalty.points_redeemed += points
        loyalty.points_balance -= points
        
        self.db.commit()
        return discount_amount
        
    def _update_tier(self, loyalty: LoyaltyPoint):
        """Update tier based on lifetime points earned."""
        total = loyalty.points_earned
        
        new_tier = 'bronze'
        if total >= self.TIER_THRESHOLDS['platinum']:
            new_tier = 'platinum'
        elif total >= self.TIER_THRESHOLDS['gold']:
            new_tier = 'gold'
        elif total >= self.TIER_THRESHOLDS['silver']:
            new_tier = 'silver'
            
        loyalty.tier = new_tier
