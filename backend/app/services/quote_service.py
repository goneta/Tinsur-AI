"""
Quote service for business logic operations.
"""
from typing import Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date, timedelta
import random

from app.models.quote import Quote
from app.models.client import Client
from app.models.policy_type import PolicyType
from app.repositories.quote_repository import QuoteRepository


class QuoteService:
    """Service for quote-related business logic."""
    
    def __init__(self, quote_repo: QuoteRepository):
        self.quote_repo = quote_repo
    
    def generate_quote_number(self, company_id: UUID, policy_type_code: str) -> str:
        """Generate unique quote number."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = random.randint(1000, 9999)
        return f"Q-{policy_type_code}-{timestamp}-{random_suffix}"
    
    def calculate_premium(
        self,
        policy_type_id: UUID,
        coverage_amount: Decimal,
        risk_factors: Dict[str, Any],
        duration_months: int = 12,
        policy_id: Optional[UUID] = None  # Added for UBI adjustment
    ) -> Dict[str, Any]:
        """
        Calculate premium based on policy type and risk factors.
        """
        # Base premium rate (percentage of coverage)
        base_rates = {
            'VEHICLE': Decimal('0.05'),
            'PROPERTY': Decimal('0.03'),
            'LIFE': Decimal('0.02'),
            'HEALTH': Decimal('0.04'),
        }
        
        base_rate = base_rates.get('VEHICLE', Decimal('0.04'))
        base_premium = coverage_amount * base_rate
        
        # Calculate risk adjustments
        risk_score = self._calculate_risk_score(risk_factors)
        risk_adjustment = base_premium * (risk_score / 100)
        
        # Adjust for duration
        duration_factor = Decimal(duration_months) / Decimal(12)
        adjusted_premium = (base_premium + risk_adjustment) * duration_factor
        
        # UBI Adjustment (Phase 7)
        ubi_adjustment_amount = Decimal('0')
        if policy_id:
            from app.services.telematics_service import TelematicsService
            from app.core.database import SessionLocal # A bit hacky to import here but for simplicity in this service
            db = SessionLocal()
            try:
                telematics_service = TelematicsService(db)
                ubi_factor = telematics_service.get_ubi_adjustment(policy_id)
                ubi_adjustment_amount = adjusted_premium * ubi_factor
            finally:
                db.close()
        
        final_premium = adjusted_premium + ubi_adjustment_amount
        
        return {
            'base_premium': base_premium,
            'risk_adjustment': risk_adjustment,
            'ubi_adjustment': ubi_adjustment_amount,
            'risk_score': risk_score,
            'final_premium': final_premium,
            'discount_amount': Decimal('0'),
            'risk_factors_analysis': self._analyze_risk_factors(risk_factors),
            'recommendations': self._generate_recommendations(risk_score, risk_factors)
        }
    
    def _calculate_risk_score(self, risk_factors: Dict[str, Any]) -> Decimal:
        """Calculate risk score from risk factors (0-100)."""
        score = Decimal('50')  # Base score
        
        # Example risk factor calculations for vehicle insurance
        if 'driver_age' in risk_factors:
            age = risk_factors['driver_age']
            if age < 25:
                score += Decimal('15')
            elif age > 60:
                score += Decimal('10')
            else:
                score -= Decimal('5')
        
        if 'accidents' in risk_factors:
            accidents = risk_factors.get('accidents', 0)
            score += Decimal(str(accidents * 10))
        
        if 'vehicle_age' in risk_factors:
            vehicle_age = risk_factors['vehicle_age']
            score += Decimal(str(vehicle_age * 2))
        
        # Ensure score is within 0-100
        return max(Decimal('0'), min(Decimal('100'), score))
    
    def _analyze_risk_factors(self, risk_factors: Dict[str, Any]) -> Dict[str, str]:
        """Analyze risk factors and provide insights."""
        analysis = {}
        
        if 'driver_age' in risk_factors:
            age = risk_factors['driver_age']
            if age < 25:
                analysis['driver_age'] = 'High risk: Young driver'
            elif age > 60:
                analysis['driver_age'] = 'Moderate risk: Senior driver'
            else:
                analysis['driver_age'] = 'Low risk: Experienced driver'
        
        if 'accidents' in risk_factors:
            accidents = risk_factors.get('accidents', 0)
            if accidents == 0:
                analysis['accidents'] = 'Excellent: No accident history'
            elif accidents <= 2:
                analysis['accidents'] = 'Moderate: Some accident history'
            else:
                analysis['accidents'] = 'High risk: Multiple accidents'
        
        return analysis
    
    def _generate_recommendations(self, risk_score: Decimal, risk_factors: Dict[str, Any]) -> list:
        """Generate recommendations based on risk profile."""
        recommendations = []
        
        if risk_score > 70:
            recommendations.append("Consider defensive driving course to reduce premium")
            recommendations.append("Install vehicle tracking device for potential discount")
        
        if risk_factors.get('accidents', 0) > 0:
            recommendations.append("Maintain clean driving record for better rates")
        
        return recommendations
    
    def create_quote(
        self,
        company_id: UUID,
        client_id: UUID,
        policy_type_id: UUID,
        coverage_amount: Decimal,
        risk_factors: Dict[str, Any],
        premium_frequency: str = 'annual',
        duration_months: int = 12,
        discount_percent: Decimal = Decimal('0'),
        created_by: UUID = None
    ) -> Quote:
        """Create a new quote with calculated premium."""
        # Calculate premium
        calculation = self.calculate_premium(
            policy_type_id,
            coverage_amount,
            risk_factors,
            duration_months
        )
        
        # Generate quote number
        quote_number = self.generate_quote_number(company_id, "AUTO")  # TODO: Get policy type code
        
        # Calculate final premium with discount
        premium_amount = calculation['final_premium']
        discount_amount = premium_amount * (discount_percent / Decimal(100))
        final_premium = premium_amount - discount_amount
        
        # Set validity (30 days from now)
        valid_until = date.today() + timedelta(days=30)
        
        # Create quote
        quote = Quote(
            company_id=company_id,
            client_id=client_id,
            policy_type_id=policy_type_id,
            quote_number=quote_number,
            coverage_amount=coverage_amount,
            premium_amount=premium_amount,
            discount_percent=discount_percent,
            final_premium=final_premium,
            premium_frequency=premium_frequency,
            duration_months=duration_months,
            risk_score=calculation['risk_score'],
            status='draft',
            valid_until=valid_until,
            details=risk_factors,
            created_by=created_by
        )
        
        return self.quote_repo.create(quote)
    
    def mark_as_sent(self, quote_id: UUID) -> Quote:
        """Mark quote as sent to client."""
        quote = self.quote_repo.get_by_id(quote_id)
        if quote:
            quote.status = 'sent'
            return self.quote_repo.update(quote)
        return None
    
    def accept_quote(self, quote_id: UUID) -> Quote:
        """Mark quote as accepted."""
        quote = self.quote_repo.get_by_id(quote_id)
        if quote and not quote.is_expired:
            quote.status = 'accepted'
            return self.quote_repo.update(quote)
        return None
    
    def reject_quote(self, quote_id: UUID) -> Quote:
        """Mark quote as rejected."""
        quote = self.quote_repo.get_by_id(quote_id)
        if quote:
            quote.status = 'rejected'
            return self.quote_repo.update(quote)
        return None
    
    def check_and_expire_quotes(self, company_id: UUID) -> int:
        """Check and mark expired quotes. Returns count of expired quotes."""
        expired_quotes = self.quote_repo.get_expired_quotes(company_id)
        count = 0
        for quote in expired_quotes:
            quote.status = 'expired'
            self.quote_repo.update(quote)
            count += 1
        return count
