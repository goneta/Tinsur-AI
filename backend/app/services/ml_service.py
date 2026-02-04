"""
ML Service for predictive analytics.
"""
from typing import Dict, Any, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.time import utcnow

from app.models.client import Client
from app.models.policy import Policy
from app.models.claim import Claim
from app.models.payment import Payment
from app.models.ticket import Ticket
from app.models.premium_schedule import PremiumSchedule

class MLService:
    """Service for handling ML-based predictions and risk scores."""
    
    def __init__(self, db: Session):
        self.db = db
        
    def predict_churn(self, client_id: UUID) -> Dict[str, Any]:
        """
        Calculate churn probability for a client.
        Logic based on Phase 7 requirements.
        """
        client = self.db.query(Client).get(client_id)
        if not client:
            raise ValueError("Client not found")
            
        policies = self.db.query(Policy).filter(Policy.client_id == client_id).all()
        if not policies:
            return {"score": 0.1, "risk_level": "low", "reason": "No active policies"}
            
        # 1. Months since first policy
        first_policy = min(p.created_at for p in policies)
        months_active = (utcnow() - first_policy).days / 30
        
        # 2. Number of claims
        claims_count = self.db.query(Claim).filter(Claim.client_id == client_id).count()
        
        # 3. Payment delays (average days overdue)
        schedules = self.db.query(PremiumSchedule).join(Policy).filter(Policy.client_id == client_id).all()
        overdue_days = 0
        overdue_count = 0
        for s in schedules:
            if s.status == 'overdue':
                overdue_days += (utcnow().date() - s.due_date).days
                overdue_count += 1
            elif s.status == 'paid' and s.paid_at and s.paid_at.date() > s.due_date:
                overdue_days += (s.paid_at.date() - s.due_date).days
                overdue_count += 1
        
        avg_delay = overdue_days / overdue_count if overdue_count > 0 else 0
        
        # 4. Support interactions
        tickets_count = self.db.query(Ticket).filter(Ticket.client_id == client_id).count()
        
        # Simple Weighted Scoring (0.0 to 1.0)
        score = Decimal('0.2') # Base score
        
        if avg_delay > 10: score += Decimal('0.3')
        elif avg_delay > 5: score += Decimal('0.15')
        
        if claims_count > 2: score += Decimal('0.2')
        if tickets_count > 3: score += Decimal('0.15')
        if months_active < 6: score += Decimal('0.1')
        
        # Cap score at 1.0
        score = min(score, Decimal('0.95'))
        
        risk_level = "low"
        if score > 0.7: risk_level = "high"
        elif score > 0.4: risk_level = "medium"
        
        return {
            "score": float(score),
            "risk_level": risk_level,
            "metrics": {
                "avg_payment_delay": avg_delay,
                "claims_count": claims_count,
                "support_tickets": tickets_count,
                "months_active": months_active
            },
            "recommendations": self._get_churn_recommendations(risk_level, avg_delay)
        }
    
    def predict_fraud(self, claim_id: UUID) -> Dict[str, Any]:
        """
        Calculate fraud risk score for a claim.
        Logic based on Phase 7 requirements.
        """
        claim = self.db.query(Claim).get(claim_id)
        if not claim:
            raise ValueError("Claim not found")
            
        policy = self.db.query(Policy).get(claim.policy_id)
        
        # 1. Claim amount vs Policy limit
        amount_ratio = claim.claim_amount / policy.coverage_amount if policy.coverage_amount > 0 else 0
        
        # 2. Time since policy start (fraud often happens shortly after inception)
        days_since_start = (claim.incident_date - policy.start_date).days
        
        # 3. Claim frequency for this client
        client_claims_count = self.db.query(Claim).filter(
            Claim.client_id == claim.client_id,
            Claim.id != claim_id
        ).count()
        
        # 4. Geolocation anomalies (placeholder logic)
        geo_anomaly = False # In a real app, compare incident location with client address
        
        # Scoring (0 to 100)
        score = 10 # Base score
        
        if days_since_start < 30: score += 30
        elif days_since_start < 90: score += 15
        
        if amount_ratio > 0.8: score += 25
        
        if client_claims_count > 1: score += 20
        
        if geo_anomaly: score += 15
        
        risk_level = "low"
        if score > 70: risk_level = "high"
        elif score > 40: risk_level = "medium"
        
        return {
            "score": score,
            "risk_level": risk_level,
            "factors": {
                "days_since_inception": days_since_start,
                "coverage_utilization": float(amount_ratio),
                "previous_claims": client_claims_count
            }
        }
        
    def _get_churn_recommendations(self, risk_level: str, avg_delay: float) -> List[str]:
        recs = []
        if risk_level == "high":
            recs.append("Trigger proactive retention call")
            recs.append("Offer loyalty discount on next renewal")
        if avg_delay > 7:
            recs.append("Review payment method and grace periods")
        return recs
