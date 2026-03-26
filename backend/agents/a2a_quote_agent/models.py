from pydantic import BaseModel, Field
from typing import Optional, List

class QuoteRequest(BaseModel):
    client_name: Optional[str] = Field(None, description="Name of the client")
    policy_type: Optional[str] = Field(None, description="Type of policy: 'Automobile', 'Housing', etc.")
    coverage_amount: Optional[float] = Field(None, description="Requested coverage amount")
    duration_months: Optional[int] = Field(None, description="Duration of the policy in months")
    payment_frequency: Optional[str] = Field(None, description="Payment frequency (e.g. Monthly, Annual)")
    vehicle_value: Optional[float] = Field(None, description="Value of the vehicle")
    vehicle_age: Optional[int] = Field(None, description="Registration year of the vehicle")
    vehicle_mileage: Optional[float] = Field(None, description="Vehicle mileage in km")
    vehicle_registration: Optional[str] = Field(None, description="Vehicle registration number")
    license_number: Optional[str] = Field(None, description="Driver licence number")
    driver_dob: Optional[str] = Field(None, description="Driver date of birth (YYYY-MM-DD)")
    manual_discount: Optional[float] = Field(0.0, description="Manual discount amount")

class QuoteResponse(BaseModel):
    quote_id: str
    premium_yearly: float
    premium_monthly: float
    details: str
    status: str = "success"
