"""
Policy-specific client detail models.
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Numeric, Date, Float, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base

class ClientAutomobile(Base):
    """Automobile specific details for a client's vehicle."""
    __tablename__ = "client_automobile"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), unique=True)
    
    # Vehicle Details
    vehicle_registration = Column(String(50))
    vehicle_make = Column(String(50))
    vehicle_model = Column(String(50))
    vehicle_year = Column(Integer)
    vehicle_value = Column(Numeric(15, 2))
    vehicle_mileage = Column(Float)
    engine_capacity_cc = Column(Integer)
    fuel_type = Column(String(50)) # petrol, diesel, electric, hybrid
    vehicle_usage = Column(String(50)) # private, commercial, taxi, delivery
    seat_count = Column(Integer)
    chassis_number = Column(String(100)) # VIN
    vehicle_color = Column(String(50))
    country_of_registration = Column(String(100))
    registration_document_url = Column(String(500), nullable=True)

    
    # Driver Details (Main Driver)
    driver_name = Column(String(100))
    driver_dob = Column(Date)
    license_number = Column(String(100))
    license_issue_date = Column(Date)
    license_expiry_date = Column(Date)
    license_category = Column(String(50))
    driving_experience_years = Column(Integer)
    
    # History
    accident_count = Column(Integer, default=0)
    claim_count = Column(Integer, default=0)
    no_claim_bonus_status = Column(String(50))
    previous_insurer = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    client = relationship("Client", back_populates="automobile_details")

class ClientHousing(Base):
    """Housing specific details for a client."""
    __tablename__ = "client_housing"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), unique=True)
    
    # Property Details
    property_type = Column(String(50)) # house, apartment, villa, commercial
    address = Column(String(255))
    city = Column(String(100))
    country = Column(String(100))
    construction_year = Column(Integer)
    property_size_sqm = Column(Float)
    room_count = Column(Integer)
    floor_count = Column(Integer)
    building_material = Column(String(100)) # concrete, wood, mixed
    occupancy_type = Column(String(50)) # owner-occupied, rented, vacant
    
    # Value
    building_value = Column(Numeric(15, 2))
    contents_value = Column(Numeric(15, 2))
    
    # Risk & Safety
    security_system = Column(Boolean, default=False)
    fire_protection = Column(Boolean, default=False)
    flood_zone = Column(Boolean, default=False)
    earthquake_zone = Column(Boolean, default=False)
    
    # Ownership
    ownership_status = Column(String(50)) # owner, tenant
    mortgage_info = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    client = relationship("Client", back_populates="housing_details")

class ClientHealth(Base):
    """Health specific details for a client."""
    __tablename__ = "client_health"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), unique=True)
    
    # Personal Health
    height_cm = Column(Float)
    weight_kg = Column(Float)
    bmi = Column(Float)
    blood_group = Column(String(10))
    smoking_status = Column(String(50))
    alcohol_consumption = Column(String(50))
    
    # Medical History
    pre_existing_conditions = Column(Text) # JSON or Comma Separated
    chronic_diseases = Column(Text)
    past_surgeries = Column(Text)
    current_medications = Column(Text)
    family_medical_history = Column(Text)
    
    # Coverage Preferences
    coverage_type = Column(String(50)) # individual, family
    dependents_list = Column(Text) # JSON list of names
    maternity_coverage = Column(Boolean, default=False)
    dental_optical_coverage = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    client = relationship("Client", back_populates="health_details")

class ClientLife(Base):
    """Life insurance specific details for a client."""
    __tablename__ = "client_life"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), unique=True)
    
    # Personal & Financial extended
    dependent_count = Column(Integer, default=0)
    annual_income = Column(Numeric(15, 2))
    source_of_income = Column(String(100))
    
    # Lifestyle & Risk
    smoking_status = Column(String(20))
    alcohol_consumption = Column(String(50))
    high_risk_activities = Column(Text) # sports, aviation etc.
    
    # Medical
    medical_history_summary = Column(Text)
    
    # Beneficiaries
    beneficiaries = Column(Text) # JSON list of objects {name, relation, percentage}
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    client = relationship("Client", back_populates="life_details")
