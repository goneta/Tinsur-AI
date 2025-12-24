"""
Telematics Service for UBI pricing.
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session

from app.models.telematics import TelematicsData
from app.models.policy import Policy

class TelematicsService:
    """Service for processing telematics data and calculating UBI adjustments."""
    
    def __init__(self, db: Session):
        self.db = db
        
    def calculate_safety_score(self, policy_id: UUID, days: int = 30) -> Decimal:
        """
        Calculate a safety score (0-100) for a policy based on recent telematics data.
        """
        data = self.db.query(TelematicsData).filter(
            TelematicsData.policy_id == policy_id
        ).order_by(TelematicsData.trip_date.desc()).limit(days).all()
        
        if not data:
            return Decimal('70.0') # Default for new or no data
            
        total_score = sum(d.safety_score for d in data)
        avg_score = total_score / len(data)
        
        # Penalize for specific events if safety_score doesn't already capture it fully
        harsh_braking = sum(d.harsh_braking_count for d in data)
        night_km = sum(d.night_driving_km for d in data)
        
        # Simple adjustment
        final_score = avg_score - (Decimal(str(harsh_braking)) * Decimal('0.5'))
        final_score -= (night_km / Decimal('100')) * Decimal('1.0')
        
        return max(Decimal('0'), min(Decimal('100'), final_score))
        
    def get_ubi_adjustment(self, policy_id: UUID) -> Decimal:
        """
        Calculate a premium adjustment percentage based on the safety score.
        Returns a value like -0.15 (15% discount) or 0.10 (10% surcharge).
        """
        score = self.calculate_safety_score(policy_id)
        
        if score > 90:
            return Decimal('-0.20') # 20% Discount
        elif score > 80:
            return Decimal('-0.10') # 10% Discount
        elif score > 60:
            return Decimal('-0.05') # 5% Discount
        elif score > 40:
            return Decimal('0.00')  # No change
        elif score > 20:
            return Decimal('0.10')  # 10% Surcharge
        else:
            return Decimal('0.25')  # 25% Surcharge
            
    def process_trip_data(self, policy_id: UUID, trip_data: Dict[str, Any]) -> TelematicsData:
        """Process and save new trip data."""
        # Calculate a basic safety score for this trip
        # Base 100
        score = 100
        score -= trip_data.get('harsh_braking_count', 0) * 5
        score -= trip_data.get('harsh_acceleration_count', 0) * 3
        
        avg_speed = trip_data.get('avg_speed', 0)
        if avg_speed > 110: score -= 20
        elif avg_speed > 90: score -= 10
        
        telematics = TelematicsData(
            policy_id=policy_id,
            device_id=trip_data.get('device_id', 'UNKNOWN'),
            trip_date=date.today(),
            distance_km=Decimal(str(trip_data.get('distance_km', 0))),
            avg_speed=Decimal(str(avg_speed)),
            max_speed=Decimal(str(trip_data.get('max_speed', 0))),
            harsh_braking_count=trip_data.get('harsh_braking_count', 0),
            harsh_acceleration_count=trip_data.get('harsh_acceleration_count', 0),
            night_driving_km=Decimal(str(trip_data.get('night_driving_km', 0))),
            safety_score=Decimal(str(max(0, score)))
        )
        
        self.db.add(telematics)
        self.db.commit()
        self.db.refresh(telematics)
        return telematics
