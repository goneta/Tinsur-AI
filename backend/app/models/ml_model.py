"""
ML Model metadata tracker.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.core.database import Base

class MLModel(Base):
    """Model to track machine learning models."""
    __tablename__ = "ml_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    
    model_name = Column(String(255), nullable=False)
    model_type = Column(String(100)) # 'churn_prediction', 'fraud_detection', 'claim_likelihood'
    model_version = Column(String(50))
    
    accuracy = Column(Numeric(5, 4))
    deployed_at = Column(DateTime)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MLModel {self.model_name} v{self.model_version}>"
