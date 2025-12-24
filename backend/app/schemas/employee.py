"""
Employee and Payroll schemas.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid
from decimal import Decimal
from app.schemas.user import UserResponse

class EmployeeProfileBase(BaseModel):
    payment_method: Optional[str] = "bank_transfer" # mobile_money, bank_transfer
    mobile_money_provider: Optional[str] = None # orange, mtn, wave, moov
    mobile_money_number: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_account_holder_name: Optional[str] = None
    iban: Optional[str] = None
    swift_bic: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    base_salary: Optional[Decimal] = None
    currency: Optional[str] = "XOF"

class EmployeeProfileCreate(EmployeeProfileBase):
    pass

class EmployeeProfileUpdate(EmployeeProfileBase):
    pass

class EmployeeCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: str # admin, manager, agent, receptionist
    company_id: Optional[uuid.UUID] = None # Optional in schema, but usually required logic-wise
    pos_location_id: Optional[uuid.UUID] = None
    created_by: Optional[uuid.UUID] = None
    profile: Optional[EmployeeProfileCreate] = None

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    pos_location_id: Optional[uuid.UUID] = None
    profile: Optional[EmployeeProfileUpdate] = None

class EmployeeProfileResponse(EmployeeProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID

    class Config:
        from_attributes = True

class POSLocationSummary(BaseModel):
    id: uuid.UUID
    name: str
    city: Optional[str] = None
    
    class Config:
        from_attributes = True

class EmployeeResponse(UserResponse):
    employee_profile: Optional[EmployeeProfileResponse] = None
    pos_location: Optional[POSLocationSummary] = None

    class Config:
        from_attributes = True

# Payroll Schemas

class PayrollTransactionBase(BaseModel):
    amount: Decimal
    currency: Optional[str] = "XOF"
    payment_method: str
    description: Optional[str] = None
    reference_number: Optional[str] = None
    payment_month: Optional[str] = None
    
    # Breakdown
    base_salary: Optional[Decimal] = 0
    transport_allowance: Optional[Decimal] = 0
    housing_allowance: Optional[Decimal] = 0
    commissions_total: Optional[Decimal] = 0
    
    # Deductions
    tax_is: Optional[Decimal] = 0
    tax_cn: Optional[Decimal] = 0
    tax_igr: Optional[Decimal] = 0
    social_security_cnps: Optional[Decimal] = 0
    net_pay: Optional[Decimal] = 0

class PayrollTransactionCreate(PayrollTransactionBase):
    employee_id: uuid.UUID

class PayrollTransactionResponse(PayrollTransactionBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    company_id: uuid.UUID
    payment_date: datetime
    payment_month: Optional[str] = None
    status: str
    failure_reason: Optional[str] = None
    processed_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    
    # Include employee name for display convenience
    employee_name: Optional[str] = None

    class Config:
        from_attributes = True

class PayrollGenerateRequest(BaseModel):
    month: str # YYYY-MM
