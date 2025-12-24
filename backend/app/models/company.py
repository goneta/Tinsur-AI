"""
Company model for multi-tenant architecture.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class Company(Base):
    """Company model for multi-tenancy."""
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    address = Column(Text)
    
    # Company registration and legal info
    registration_number = Column(String(100))
    
    # Financial information
    bank_details = Column(JSON, default=[])  # List of bank accounts
    mobile_money_accounts = Column(JSON, default=[])  # List of mobile money accounts
    
    # Regional settings
    currency = Column(String(10), default="USD")
    country = Column(String(100))
    timezone = Column(String(50), default="UTC")
    
    is_active = Column(Boolean, default=True)
    
    # Settings (JSON)
    # logo_url = Column(String) # Moved to base user or kept? Company logo.
    logo_url = Column(String, nullable=True)
    primary_color = Column(String(10), nullable=True) # Hex code
    secondary_color = Column(String(10), nullable=True) # Hex code
    theme_colors = Column(String, nullable=True) # Legacy or combined JSON
    
    # Modules/Features enabled
    features = Column(JSON, default={})
    
    # AI Subscription & Quotas
    # Plans: 'BASIC', 'BYOK', 'CREDIT'
    ai_plan = Column(String(20), default="CREDIT") 
    ai_api_key_encrypted = Column(String(500), nullable=True) # For BYOK Plan
    ai_credits_balance = Column(Float, default=100.0) # For CREDIT Plan
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="company", cascade="all, delete-orphan")
    
    # Documents
    documents = relationship("Document", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company {self.name}>"
