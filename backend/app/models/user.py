"""
User model for authentication and authorization.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
import uuid
from app.core.guid import GUID
from datetime import datetime

from app.core.database import Base


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(50))
    user_type = Column(String(50), nullable=False)  # 'super_admin', 'company_admin', 'manager', 'agent', 'client'
    pos_location_id = Column(GUID(), ForeignKey("pos_locations.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))
    profile_picture = Column(String(500), nullable=True)
    compliance_status = Column(String(50), default="pending")  # 'pending', 'approved', 'flagged'
    is_high_risk = Column(Boolean, default=False)
    compliance_notes = Column(Text, nullable=True)
    underwriting_limit = Column(Numeric(15, 2), default=0.00)
    last_login = Column(DateTime)
    created_by = Column(GUID(), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="users")
    pos_location = relationship("POSLocation", back_populates="employees", foreign_keys=[pos_location_id])
    creator = relationship("User", remote_side=[id], foreign_keys=[created_by])
    
    @property
    def role(self):
        """Alias for user_type for backward compatibility."""
        return self.user_type

    @role.setter
    def role(self, value):
        """Setter for role that updates user_type."""
        self.user_type = value
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    @property
    def full_name(self):
        """Get full name."""
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.email
    @property
    def primary_color(self):
        """Get company primary color."""
        return self.company.primary_color if self.company else None

    @property
    def secondary_color(self):
        """Get company secondary color."""
        return self.company.secondary_color if self.company else None

    @property
    def company_logo_url(self):
        """Get company logo URL."""
        return self.company.logo_url if self.company else None
