"""
Underwriting models for authority, referrals, deterministic quote decisions, and quote snapshots.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Numeric, Integer, Boolean, Date, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.time import utcnow

from app.core.database import Base
from app.core.guid import GUID

class UnderwritingReferral(Base):
    """
    Tracks quotes that require manual underwriting approval.
    """
    __tablename__ = "underwriting_referrals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    quote_id = Column(UUID(as_uuid=True), ForeignKey("quotes.id", ondelete="CASCADE"), nullable=True, unique=True)
    endorsement_id = Column(UUID(as_uuid=True), ForeignKey("endorsements.id", ondelete="CASCADE"), nullable=True, unique=True)
    
    referred_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    status = Column(String(50), default='pending') # 'pending', 'approved', 'rejected'
    reason = Column(String(500)) # e.g., "Exceeds authority limit ($10k)"
    decision_notes = Column(Text)
    
    decided_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    decided_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    company = relationship("Company")
    quote = relationship("Quote")
    endorsement = relationship("Endorsement")
    referrer = relationship("User", foreign_keys=[referred_by_id])
    assignee = relationship("User", foreign_keys=[assigned_to_id])
    decider = relationship("User", foreign_keys=[decided_by_id])


class Vehicle(Base):
    """Normalized quote-time vehicle profile used by deterministic automobile underwriting."""
    __tablename__ = "vehicles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(GUID(), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    client_automobile_id = Column(GUID(), ForeignKey("client_automobile.id", ondelete="SET NULL"), nullable=True)

    registration_number = Column(String(50), nullable=True, index=True)
    vin = Column(String(100), nullable=True, index=True)
    make = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    variant = Column(String(100), nullable=True)
    year = Column(Integer, nullable=False)
    body_type = Column(String(75), nullable=True)
    fuel_type = Column(String(50), nullable=True)
    transmission = Column(String(50), nullable=True)
    engine_size_cc = Column(Integer, nullable=True)
    seat_count = Column(Integer, nullable=True)
    market_value = Column(Numeric(15, 2), nullable=False)
    annual_mileage = Column(Integer, nullable=True)
    usage_class = Column(String(75), nullable=False)
    garaging_postcode = Column(String(30), nullable=True)
    garaging_region = Column(String(100), nullable=True)
    overnight_parking = Column(String(100), nullable=True)
    security_devices = Column(JSON, default=list)
    modifications = Column(JSON, default=list)
    imported = Column(Boolean, default=False)
    prior_damage = Column(Boolean, default=False)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company")
    client = relationship("Client")
    client_automobile = relationship("ClientAutomobile")
    drivers = relationship("Driver", back_populates="vehicle", cascade="all, delete-orphan")
    risk_profile = relationship("VehicleRiskProfile", back_populates="vehicle", uselist=False, cascade="all, delete-orphan")


class Driver(Base):
    """Normalized quote-time driver profile linked to a vehicle and optional client driver record."""
    __tablename__ = "drivers"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(GUID(), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    vehicle_id = Column(GUID(), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=True, index=True)
    client_driver_id = Column(GUID(), ForeignKey("client_drivers.id", ondelete="SET NULL"), nullable=True)

    is_primary = Column(Boolean, default=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    licence_type = Column(String(75), nullable=True)
    licence_issue_date = Column(Date, nullable=True)
    years_licensed = Column(Integer, default=0)
    occupation = Column(String(150), nullable=True)
    marital_status = Column(String(50), nullable=True)
    address_postcode = Column(String(30), nullable=True)
    address_region = Column(String(100), nullable=True)
    no_claim_discount_years = Column(Integer, default=0)
    no_claim_discount_protected = Column(Boolean, default=False)
    previous_insurer = Column(String(150), nullable=True)
    cancellation_or_refusal_history = Column(Boolean, default=False)
    relationship_to_policyholder = Column(String(75), nullable=True)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company")
    client = relationship("Client")
    vehicle = relationship("Vehicle", back_populates="drivers")
    client_driver = relationship("ClientDriver")
    claims = relationship("DriverClaimHistory", back_populates="driver", cascade="all, delete-orphan")
    convictions = relationship("DriverConvictionHistory", back_populates="driver", cascade="all, delete-orphan")


class DriverClaimHistory(Base):
    """Claim history item used in deterministic driver underwriting."""
    __tablename__ = "driver_claim_history"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    driver_id = Column(GUID(), ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_date = Column(Date, nullable=True)
    claim_type = Column(String(100), nullable=True)
    amount = Column(Numeric(15, 2), default=0)
    at_fault = Column(Boolean, default=False)
    settled = Column(Boolean, default=True)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utcnow)
    driver = relationship("Driver", back_populates="claims")


class DriverConvictionHistory(Base):
    """Conviction or violation history item used in deterministic driver underwriting."""
    __tablename__ = "driver_conviction_history"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    driver_id = Column(GUID(), ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False, index=True)
    conviction_date = Column(Date, nullable=True)
    code = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    points = Column(Integer, default=0)
    severity = Column(String(50), default="minor")

    created_at = Column(DateTime, default=utcnow)
    driver = relationship("Driver", back_populates="convictions")


class VehicleRiskProfile(Base):
    """Normalized vehicle risk profile calculated from vehicle, usage, location, and driver context."""
    __tablename__ = "vehicle_risk_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(GUID(), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, unique=True)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    risk_group = Column(String(75), default="standard")
    risk_score = Column(Numeric(5, 2), default=0)
    factors = Column(JSON, default=dict)
    reason_codes = Column(JSON, default=list)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    vehicle = relationship("Vehicle", back_populates="risk_profile")
    company = relationship("Company")


class UnderwritingRuleSet(Base):
    """Versioned rule set for deterministic underwriting and rating decisions."""
    __tablename__ = "underwriting_rule_sets"
    __table_args__ = (UniqueConstraint("company_id", "version", name="uq_underwriting_rule_sets_company_version"),)

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    version = Column(String(50), nullable=False)
    status = Column(String(50), default="active")
    effective_from = Column(DateTime, nullable=True)
    effective_to = Column(DateTime, nullable=True)
    default_base_rate = Column(Numeric(8, 5), default=0.045)
    configuration = Column(JSON, default=dict)
    created_by_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    approved_by_id = Column(GUID(), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company")
    created_by = relationship("User", foreign_keys=[created_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    rules = relationship("UnderwritingRule", back_populates="rule_set", cascade="all, delete-orphan")


class UnderwritingRule(Base):
    """Single deterministic underwriting or rating rule within a versioned rule set."""
    __tablename__ = "underwriting_rules"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    rule_set_id = Column(GUID(), ForeignKey("underwriting_rule_sets.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(100), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    category = Column(String(75), nullable=False)
    priority = Column(Integer, default=100)
    decision_effect = Column(String(50), default="rate")
    condition = Column(JSON, default=dict)
    rate_effect = Column(JSON, default=dict)
    message = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    rule_set = relationship("UnderwritingRuleSet", back_populates="rules")


class UnderwritingDecision(Base):
    """Persisted deterministic underwriting decision for a quote intake payload."""
    __tablename__ = "underwriting_decisions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    quote_id = Column(GUID(), ForeignKey("quotes.id", ondelete="CASCADE"), nullable=True, index=True)
    rule_set_id = Column(GUID(), ForeignKey("underwriting_rule_sets.id", ondelete="SET NULL"), nullable=True)

    decision = Column(String(50), nullable=False)
    status = Column(String(50), default="final")
    base_premium = Column(Numeric(15, 2), default=0)
    final_premium = Column(Numeric(15, 2), default=0)
    risk_score = Column(Numeric(5, 2), default=0)
    breakdown = Column(JSON, default=dict)
    referral_reasons = Column(JSON, default=list)
    decline_reasons = Column(JSON, default=list)
    required_documents = Column(JSON, default=list)
    warnings = Column(JSON, default=list)
    assumptions = Column(JSON, default=list)
    rule_matches = Column(JSON, default=list)
    input_snapshot = Column(JSON, default=dict)

    decided_at = Column(DateTime, default=utcnow)
    created_at = Column(DateTime, default=utcnow)

    company = relationship("Company")
    quote = relationship("Quote")
    rule_set = relationship("UnderwritingRuleSet")
    quote_snapshot = relationship("QuoteUnderwritingSnapshot", back_populates="decision", uselist=False)


class QuoteUnderwritingSnapshot(Base):
    """Immutable quote snapshot used later for payment and policy issuance revalidation."""
    __tablename__ = "quote_underwriting_snapshots"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    quote_id = Column(GUID(), ForeignKey("quotes.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    underwriting_decision_id = Column(GUID(), ForeignKey("underwriting_decisions.id", ondelete="SET NULL"), nullable=True)
    rule_set_id = Column(GUID(), ForeignKey("underwriting_rule_sets.id", ondelete="SET NULL"), nullable=True)

    normalized_payload = Column(JSON, default=dict)
    decision_snapshot = Column(JSON, default=dict)
    premium_breakdown = Column(JSON, default=dict)
    policy_ready_payload = Column(JSON, default=dict)
    valid_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company")
    quote = relationship("Quote")
    decision = relationship("UnderwritingDecision", back_populates="quote_snapshot")
    rule_set = relationship("UnderwritingRuleSet")
