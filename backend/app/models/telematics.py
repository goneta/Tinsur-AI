"""
Telematics model for usage-based insurance data.
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base

class TelematicsData(Base):
    """Telematics data model."""
    __tablename__ = "telematics_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"))
    
    device_id = Column(String(255), nullable=False)
    trip_date = Column(Date, nullable=False)
    
    distance_km = Column(Numeric(10, 2))
    avg_speed = Column(Numeric(5, 2))
    max_speed = Column(Numeric(5, 2))
    
    harsh_braking_count = Column(Integer, default=0)
    harsh_acceleration_count = Column(Integer, default=0)
    
    night_driving_km = Column(Numeric(10, 2))
    safety_score = Column(Numeric(5, 2))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    policy = relationship("Policy")
    
    def __repr__(self):
        return f"<TelematicsData {self.device_id} {self.trip_date}>"
