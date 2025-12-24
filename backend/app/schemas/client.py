"""
Client schemas.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
import uuid
from decimal import Decimal

# --- Detail Schemas ---

class ClientAutomobileBase(BaseModel):
    vehicle_registration: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[int] = None
    vehicle_value: Optional[Decimal] = None
    vehicle_mileage: Optional[float] = None
    engine_capacity_cc: Optional[int] = None
    fuel_type: Optional[str] = None
    vehicle_usage: Optional[str] = None
    seat_count: Optional[int] = None
    chassis_number: Optional[str] = None
    vehicle_color: Optional[str] = None
    country_of_registration: Optional[str] = None
    registration_document_url: Optional[str] = None
    
    driver_name: Optional[str] = None
    driver_dob: Optional[date] = None
    license_number: Optional[str] = None
    license_issue_date: Optional[date] = None
    license_expiry_date: Optional[date] = None
    license_category: Optional[str] = None
    driving_experience_years: Optional[int] = None
    
    accident_count: Optional[int] = 0
    claim_count: Optional[int] = 0
    no_claim_bonus_status: Optional[str] = None
    previous_insurer: Optional[str] = None
    
class ClientAutomobileCreate(ClientAutomobileBase):
    pass

class ClientAutomobileUpdate(ClientAutomobileBase):
    pass
    
class ClientAutomobileResponse(ClientAutomobileBase):
    id: uuid.UUID
    client_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


class ClientHousingBase(BaseModel):
    property_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    construction_year: Optional[int] = None
    property_size_sqm: Optional[float] = None
    room_count: Optional[int] = None
    floor_count: Optional[int] = None
    building_material: Optional[str] = None
    occupancy_type: Optional[str] = None
    
    building_value: Optional[Decimal] = None
    contents_value: Optional[Decimal] = None
    
    security_system: bool = False
    fire_protection: bool = False
    flood_zone: bool = False
    earthquake_zone: bool = False
    
    ownership_status: Optional[str] = None
    mortgage_info: Optional[str] = None

class ClientHousingCreate(ClientHousingBase):
    pass

class ClientHousingUpdate(ClientHousingBase):
    pass

class ClientHousingResponse(ClientHousingBase):
    id: uuid.UUID
    client_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


class ClientHealthBase(BaseModel):
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    blood_group: Optional[str] = None
    smoking_status: Optional[str] = None
    alcohol_consumption: Optional[str] = None
    
    pre_existing_conditions: Optional[str] = None
    chronic_diseases: Optional[str] = None
    past_surgeries: Optional[str] = None
    current_medications: Optional[str] = None
    family_medical_history: Optional[str] = None
    
    coverage_type: Optional[str] = None
    dependents_list: Optional[str] = None
    maternity_coverage: bool = False
    dental_optical_coverage: bool = False

class ClientHealthCreate(ClientHealthBase):
    pass

class ClientHealthUpdate(ClientHealthBase):
    pass

class ClientHealthResponse(ClientHealthBase):
    id: uuid.UUID
    client_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


class ClientLifeBase(BaseModel):
    dependent_count: int = 0
    annual_income: Optional[Decimal] = None
    source_of_income: Optional[str] = None
    
    smoking_status: Optional[str] = None
    alcohol_consumption: Optional[str] = None
    high_risk_activities: Optional[str] = None
    
    medical_history_summary: Optional[str] = None
    beneficiaries: Optional[str] = None

class ClientLifeCreate(ClientLifeBase):
    pass

class ClientLifeUpdate(ClientLifeBase):
    pass

class ClientLifeResponse(ClientLifeBase):
    id: uuid.UUID
    client_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


# --- Main Client Schemas ---

class ClientBase(BaseModel):
    """Base client schema."""
    client_type: str  # 'individual' or 'corporate'
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    business_name: Optional[str] = None
    email: EmailStr
    phone: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Côte d'Ivoire"
    profile_picture: Optional[str] = None
    
    # New Fields
    nationality: Optional[str] = None
    id_number: Optional[str] = None
    id_expiry_date: Optional[date] = None
    marital_status: Optional[str] = None
    
    occupation: Optional[str] = None
    employer_name: Optional[str] = None
    employment_status: Optional[str] = None
    annual_income: Optional[Decimal] = None
    
    kyc_status: str = 'pending'
    pep_status: bool = False
    consent_accepted: bool = False
    
    driving_licence_number: Optional[str] = None
    id_card_url: Optional[str] = None
    driving_license_url: Optional[str] = None
    tax_id: Optional[str] = None
    risk_profile: str = "medium"


class ClientCreate(ClientBase):
    """Client creation schema."""
    company_id: Optional[uuid.UUID] = None
    created_by: Optional[uuid.UUID] = None


class ClientUpdate(BaseModel):
    """Client update schema."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    business_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    profile_picture: Optional[str] = None
    
    nationality: Optional[str] = None
    id_number: Optional[str] = None
    id_expiry_date: Optional[date] = None
    marital_status: Optional[str] = None
    
    occupation: Optional[str] = None
    employer_name: Optional[str] = None
    employment_status: Optional[str] = None
    annual_income: Optional[Decimal] = None
    
    kyc_status: Optional[str] = None
    pep_status: bool = False
    consent_accepted: bool = False
    
    driving_licence_number: Optional[str] = None
    id_card_url: Optional[str] = None
    driving_license_url: Optional[str] = None
    tax_id: Optional[str] = None
    risk_profile: Optional[str] = None
    status: Optional[str] = None


class ClientInDB(ClientBase):
    """Client in database schema."""
    id: uuid.UUID
    company_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    status: str = "active"
    created_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ClientResponse(ClientInDB):
    """Client response schema."""
    # Optional details inclusions
    automobile_details: Optional[ClientAutomobileResponse] = None
    housing_details: Optional[ClientHousingResponse] = None
    health_details: Optional[ClientHealthResponse] = None
    life_details: Optional[ClientLifeResponse] = None
