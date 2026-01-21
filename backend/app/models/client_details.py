"""
Policy-specific client detail models.
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Numeric, Date, Float, Boolean, Text
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base
from app.core.guid import GUID

class ClientAutomobile(Base):
    """Automobile specific details for a client's vehicle."""
    __tablename__ = "client_automobile"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    client_id = Column(GUID(), ForeignKey("clients.id", ondelete="CASCADE"))
    
    # Vehicle Details
    vehicle_registration = Column(String(50), nullable=True)
    vehicle_make = Column(String(50), nullable=True)
    vehicle_model = Column(String(50), nullable=True)
    vehicle_year = Column(Integer, nullable=True)
    vehicle_value = Column(Numeric(15, 2), nullable=True)
    vehicle_mileage = Column(Float, nullable=True)
    engine_capacity_cc = Column(Integer, nullable=True)
    fuel_type = Column(String(50), nullable=True) # petrol, diesel, electric, hybrid
    vehicle_usage = Column(String(50), nullable=True) # private, commercial, taxi, delivery
    seat_count = Column(Integer, nullable=True)
    chassis_number = Column(String(100), nullable=True) # VIN
    vehicle_color = Column(String(50), nullable=True)
    country_of_registration = Column(String(100), nullable=True)
    registration_document_url = Column(String(500), nullable=True)
    parked_location = Column(String(100), nullable=True)
    vehicle_image_url = Column(String(500), nullable=True)

    
    # Driver Details (Main Driver)
    last_name = Column(String(100), nullable=True) # Name
    first_name = Column(String(100), nullable=True) # Forenames
    driver_dob = Column(Date, nullable=True)
    license_number = Column(String(100), nullable=True)
    license_issue_date = Column(Date, nullable=True)
    license_expiry_date = Column(Date, nullable=True)
    license_category = Column(String(50), nullable=True)
    driving_experience_years = Column(Integer, nullable=True)
    
    # History
    accident_count = Column(Integer, default=0, nullable=True)
    claim_count = Column(Integer, default=0, nullable=True)
    no_claim_bonus_status = Column(String(50), nullable=True)
    previous_insurer = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    client = relationship("Client", back_populates="automobile_details")

class ClientHousing(Base):
    """Housing specific details for a client."""
    __tablename__ = "client_housing"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    client_id = Column(GUID(), ForeignKey("clients.id", ondelete="CASCADE"), unique=True)
    
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
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    client_id = Column(GUID(), ForeignKey("clients.id", ondelete="CASCADE"), unique=True)
    
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
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    client_id = Column(GUID(), ForeignKey("clients.id", ondelete="CASCADE"), unique=True)
    
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

class ClientDriver(Base):
    """Driver details associated with a client account."""
    __tablename__ = "client_drivers"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    client_id = Column(GUID(), ForeignKey("clients.id", ondelete="CASCADE"))
    
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone_number = Column(String(50))
    
    address = Column(String(255))
    city = Column(String(100))
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100))
    
    license_number = Column(String(100))
    license_issue_date = Column(Date)
    employment_status = Column(String(50))
    marital_status = Column(String(50))
    number_of_children = Column(Integer, default=0)
    photo_url = Column(String(500), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    
    # New Fields
    license_type = Column(String(50), nullable=True)
    cars_in_household = Column(Integer, default=0)
    residential_status = Column(String(50), nullable=True)
    accident_count = Column(Integer, default=0)
    no_claims_years = Column(Integer, default=0)
    driving_license_years = Column(Integer, default=0)

    is_main_driver = Column(Boolean, default=False)
    driving_license_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    client = relationship("Client", back_populates="drivers")
