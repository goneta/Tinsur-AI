"""
Client model for insurance clients.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Date, Text, Numeric, JSON, Integer, Table, select
from sqlalchemy.orm import relationship
import uuid
from app.core.guid import GUID
from datetime import datetime
from app.core.time import utcnow

from app.core.database import Base
from sqlalchemy.ext.hybrid import hybrid_property


# Junction table for many-to-many relationship between clients and companies
client_company = Table(
    'client_company',
    Base.metadata,
    Column('client_id', GUID(), ForeignKey('clients.id', ondelete='CASCADE'), primary_key=True),
    Column('company_id', GUID(), ForeignKey('companies.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=utcnow)
)


class Client(Base):
    """Client model."""
    __tablename__ = "clients"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    client_type = Column(String(50), nullable=False)  # 'individual', 'corporate'
    first_name = Column(String(100))
    last_name = Column(String(100))
    business_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    date_of_birth = Column(Date)
    gender = Column(String(20))
    profile_picture = Column(String(500), nullable=True)
    country = Column(String(100), default='Côte d\'Ivoire')
    
    # Identity
    nationality = Column(String(100))
    id_number = Column(String(100))
    id_expiry_date = Column(Date)
    marital_status = Column(String(50))
    
    # Contact
    address = Column(Text)
    city = Column(String(100))
    
    # Professional & Financial
    occupation = Column(String(100))
    employer_name = Column(String(100))
    employment_status = Column(String(50)) # employed, self-employed, unemployed, retired
    annual_income = Column(Numeric(15, 2)) # Stored as annual amount
    
    # Compliance
    kyc_status = Column(String(50), default='pending') # pending, verified, rejected
    kyc_notes = Column(Text, nullable=True) # AI remarks/rejection reasons
    kyc_results = Column(JSON, default={}) # Extracted JSON data (name, number, expiry, etc.)
    pep_status = Column(Boolean, default=False)
    consent_accepted = Column(Boolean, default=False)
    
    driving_licence_number = Column(String(100))
    # Eligibility Fields
    accident_count = Column(Integer, default=0)
    no_claims_years = Column(Integer, default=0)
    driving_license_years = Column(Integer, default=0)
    number_of_accidents_at_fault = Column(Integer, default=0)  # Required for quote creation
    
    id_card_url = Column(String(500), nullable=True)
    driving_license_url = Column(String(500), nullable=True)
    tax_id = Column(String(100))
    risk_profile = Column(String(50), default='medium')  # 'low', 'medium', 'high'
    compliance_status = Column(String(50), default='pending')  # 'pending', 'approved', 'flagged'
    is_high_risk = Column(Boolean, default=False)
    compliance_notes = Column(Text, nullable=True)
    status = Column(String(50), default='active')  # 'active', 'inactive', 'suspended'
    created_by = Column(GUID(), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    # Many-to-many with companies via junction table
    companies = relationship("Company", secondary="client_company", back_populates="clients")
    creator = relationship("User", foreign_keys=[created_by])
    
    # Detail Relationships (One-to-One)
    housing_details = relationship("ClientHousing", uselist=False, back_populates="client", cascade="all, delete-orphan")
    health_details = relationship("ClientHealth", uselist=False, back_populates="client", cascade="all, delete-orphan")
    life_details = relationship("ClientLife", uselist=False, back_populates="client", cascade="all, delete-orphan")
    
    # Detail Relationships (One-to-Many)
    automobile_details = relationship("ClientAutomobile", uselist=True, back_populates="client", cascade="all, delete-orphan")
    drivers = relationship("ClientDriver", uselist=True, back_populates="client", cascade="all, delete-orphan")
    
    def __repr__(self):
        if self.client_type == 'individual':
            return f"<Client {self.first_name} {self.last_name}>"
        return f"<Client {self.business_name}>"
    
    @property
    def display_name(self):
        """Get display name."""
        if self.client_type == 'individual':
            return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.email
        return self.business_name or self.email

    @hybrid_property
    def company_id(self):
        if getattr(self, 'companies', None):
            return self.companies[0].id
        return None

    @company_id.expression
    def company_id(cls):
        return (
            select(client_company.c.company_id)
            .where(client_company.c.client_id == cls.id)
            .limit(1)
            .scalar_subquery()
        )

    @property
    def company_ids(self):
        return [company.id for company in self.companies] if self.companies else []
