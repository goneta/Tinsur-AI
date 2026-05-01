"""Pydantic schemas for structured automobile quote intake and deterministic underwriting output."""
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UnderwritingClientInput(BaseModel):
    client_id: UUID
    policyholder_type: str = Field(default="individual")
    postcode: Optional[str] = None
    region: Optional[str] = None
    consent_to_underwrite: bool = Field(default=True)


class UnderwritingVehicleInput(BaseModel):
    client_automobile_id: Optional[UUID] = None
    registration_number: Optional[str] = None
    vin: Optional[str] = None
    make: str
    model: str
    variant: Optional[str] = None
    year: int = Field(..., ge=1900, le=2100)
    body_type: Optional[str] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    engine_size_cc: Optional[int] = Field(default=None, ge=0)
    seat_count: Optional[int] = Field(default=None, ge=1)
    market_value: Decimal = Field(..., ge=Decimal("0"), multiple_of=Decimal("0.01"))
    annual_mileage: Optional[int] = Field(default=None, ge=0)
    usage_class: str = Field(default="private")
    garaging_postcode: Optional[str] = None
    garaging_region: Optional[str] = None
    overnight_parking: Optional[str] = None
    security_devices: List[str] = Field(default_factory=list)
    modifications: List[str] = Field(default_factory=list)
    imported: bool = False
    prior_damage: bool = False


class DriverClaimHistoryInput(BaseModel):
    claim_date: Optional[date] = None
    claim_type: Optional[str] = None
    amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"), multiple_of=Decimal("0.01"))
    at_fault: bool = False
    settled: bool = True
    description: Optional[str] = None


class DriverConvictionHistoryInput(BaseModel):
    conviction_date: Optional[date] = None
    code: Optional[str] = None
    description: Optional[str] = None
    points: int = Field(default=0, ge=0)
    severity: str = Field(default="minor")


class UnderwritingDriverInput(BaseModel):
    client_driver_id: Optional[UUID] = None
    is_primary: bool = False
    first_name: str
    last_name: str
    date_of_birth: date
    licence_type: Optional[str] = None
    licence_issue_date: Optional[date] = None
    years_licensed: int = Field(default=0, ge=0)
    occupation: Optional[str] = None
    marital_status: Optional[str] = None
    address_postcode: Optional[str] = None
    address_region: Optional[str] = None
    no_claim_discount_years: int = Field(default=0, ge=0, le=30)
    no_claim_discount_protected: bool = False
    previous_insurer: Optional[str] = None
    cancellation_or_refusal_history: bool = False
    relationship_to_policyholder: Optional[str] = None
    claims_history: List[DriverClaimHistoryInput] = Field(default_factory=list)
    conviction_history: List[DriverConvictionHistoryInput] = Field(default_factory=list)


class UnderwritingUsageInput(BaseModel):
    cover_start_date: Optional[date] = None
    policy_duration_months: int = Field(default=12, ge=1, le=120)
    use_class: str = Field(default="private")
    commuting: bool = False
    business_use: bool = False
    delivery_or_rideshare: bool = False
    annual_mileage_band: Optional[str] = None
    telematics_consent: bool = False


class UnderwritingCoverOptionsInput(BaseModel):
    policy_type_id: UUID
    coverage_amount: Decimal = Field(..., ge=Decimal("0"), multiple_of=Decimal("0.01"))
    voluntary_excess: Decimal = Field(default=Decimal("0"), ge=Decimal("0"), multiple_of=Decimal("0.01"))
    cover_level: str = Field(default="comprehensive")
    add_ons: List[str] = Field(default_factory=list)


class UnderwritingNcdInput(BaseModel):
    years: int = Field(default=0, ge=0, le=30)
    protected: bool = False
    proof_available: bool = False
    previous_insurer: Optional[str] = None


class UnderwritingPaymentTermsInput(BaseModel):
    premium_frequency: str = Field(default="annual")
    payment_method: Optional[str] = None
    finance_requested: bool = False


class StructuredQuoteIntakeRequest(BaseModel):
    client: UnderwritingClientInput
    vehicle: UnderwritingVehicleInput
    drivers: List[UnderwritingDriverInput] = Field(..., min_length=1)
    usage: UnderwritingUsageInput = Field(default_factory=UnderwritingUsageInput)
    cover_options: UnderwritingCoverOptionsInput
    ncd: UnderwritingNcdInput = Field(default_factory=UnderwritingNcdInput)
    payment_terms: UnderwritingPaymentTermsInput = Field(default_factory=UnderwritingPaymentTermsInput)
    quote_id: Optional[UUID] = None
    persist_quote: bool = Field(default=True)

    @field_validator("drivers")
    @classmethod
    def must_have_primary_driver(cls, drivers: List[UnderwritingDriverInput]):
        if not any(driver.is_primary for driver in drivers):
            drivers[0].is_primary = True
        return drivers


class UnderwritingDecisionResponse(BaseModel):
    decision: Literal["accept", "refer", "decline"]
    quote_id: Optional[UUID] = None
    underwriting_decision_id: Optional[UUID] = None
    snapshot_id: Optional[UUID] = None
    rule_version_id: Optional[UUID] = None
    base_premium: Decimal
    final_premium: Decimal
    risk_score: Decimal
    breakdown: Dict[str, Any]
    referral_reasons: List[Dict[str, Any]] = Field(default_factory=list)
    decline_reasons: List[Dict[str, Any]] = Field(default_factory=list)
    required_documents: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[Dict[str, Any]] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    rule_matches: List[Dict[str, Any]] = Field(default_factory=list)
    normalized_payload: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
