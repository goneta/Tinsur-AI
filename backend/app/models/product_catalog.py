"""
Versioned product and coverage catalog models for car, travel, and home insurance.

Milestone 4 introduces a tenant-scoped product engine that stores active product
versions, coverage definitions, selectable limits/deductibles, rating factors,
underwriting rules, and quote-wizard schemas. The deterministic rating and
underwriting services can consume these tables without hard-coding product
structure into quote endpoints.
"""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.guid import GUID
from app.core.time import utcnow


class InsuranceProduct(Base):
    """Tenant-scoped insurance product family such as car, travel, or home."""

    __tablename__ = "insurance_products"
    __table_args__ = (
        UniqueConstraint("company_id", "code", name="uq_insurance_products_company_code"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    product_line = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active", index=True)
    is_active = Column(Boolean, default=True, index=True)
    display_order = Column(Integer, default=100)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company")
    versions = relationship("ProductVersion", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<InsuranceProduct {self.code}>"


class ProductVersion(Base):
    """Effective-dated version of a product's coverage and configuration."""

    __tablename__ = "insurance_product_versions"
    __table_args__ = (
        UniqueConstraint("company_id", "product_id", "version", name="uq_product_versions_company_product_version"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(GUID(), ForeignKey("insurance_products.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    status = Column(String(50), default="draft", index=True)
    effective_from = Column(DateTime, nullable=True)
    effective_to = Column(DateTime, nullable=True)
    base_currency = Column(String(10), default="USD")
    rating_strategy = Column(String(75), default="factor_table")
    base_rate = Column(Numeric(10, 6), default=0)
    minimum_premium = Column(Numeric(15, 2), default=0)
    taxes_and_fees = Column(JSON, default=list)
    configuration = Column(JSON, default=dict)
    approved_by_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    created_by_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company")
    product = relationship("InsuranceProduct", back_populates="versions")
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    coverages = relationship("CoverageDefinition", back_populates="product_version", cascade="all, delete-orphan")
    rating_factors = relationship("RatingFactor", back_populates="product_version", cascade="all, delete-orphan")
    underwriting_rules = relationship("ProductUnderwritingRule", back_populates="product_version", cascade="all, delete-orphan")
    wizard_schemas = relationship("QuoteWizardSchema", back_populates="product_version", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ProductVersion {self.version} product={self.product_id}>"


class CoverageDefinition(Base):
    """Coverage module available under a specific product version."""

    __tablename__ = "product_coverages"
    __table_args__ = (
        UniqueConstraint("product_version_id", "code", name="uq_product_coverages_version_code"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    product_version_id = Column(GUID(), ForeignKey("insurance_product_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(75), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    coverage_type = Column(String(75), nullable=False)
    description = Column(Text, nullable=True)
    is_required = Column(Boolean, default=False)
    default_limit = Column(Numeric(15, 2), nullable=True)
    minimum_limit = Column(Numeric(15, 2), nullable=True)
    maximum_limit = Column(Numeric(15, 2), nullable=True)
    default_deductible = Column(Numeric(15, 2), nullable=True)
    exclusions = Column(JSON, default=list)
    conditions = Column(JSON, default=list)
    display_order = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company")
    product_version = relationship("ProductVersion", back_populates="coverages")
    options = relationship("CoverageOption", back_populates="coverage", cascade="all, delete-orphan")


class CoverageOption(Base):
    """Selectable limit, deductible, extension, or package option for coverage."""

    __tablename__ = "product_coverage_options"
    __table_args__ = (
        UniqueConstraint("coverage_id", "code", name="uq_product_coverage_options_coverage_code"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    coverage_id = Column(GUID(), ForeignKey("product_coverages.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(75), nullable=False, index=True)
    label = Column(String(150), nullable=False)
    option_type = Column(String(50), default="limit")
    limit_amount = Column(Numeric(15, 2), nullable=True)
    deductible_amount = Column(Numeric(15, 2), nullable=True)
    premium_delta = Column(Numeric(15, 2), default=0)
    rate_multiplier = Column(Numeric(10, 6), default=1)
    configuration = Column(JSON, default=dict)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=100)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company")
    coverage = relationship("CoverageDefinition", back_populates="options")


class RatingFactor(Base):
    """Configurable factor used by product-specific rating calculations."""

    __tablename__ = "product_rating_factors"
    __table_args__ = (
        UniqueConstraint("product_version_id", "code", name="uq_product_rating_factors_version_code"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    product_version_id = Column(GUID(), ForeignKey("insurance_product_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(100), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    factor_type = Column(String(75), nullable=False)
    applies_to = Column(String(75), nullable=False)
    input_path = Column(String(255), nullable=False)
    operator = Column(String(50), default="equals")
    value = Column(String(255), nullable=True)
    factor = Column(Numeric(10, 6), default=1)
    amount = Column(Numeric(15, 2), default=0)
    priority = Column(Integer, default=100)
    configuration = Column(JSON, default=dict)
    reason_code = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company")
    product_version = relationship("ProductVersion", back_populates="rating_factors")


class ProductUnderwritingRule(Base):
    """Product-version eligibility and referral rule for underwriting decisions."""

    __tablename__ = "product_underwriting_rules"
    __table_args__ = (
        UniqueConstraint("product_version_id", "code", name="uq_product_underwriting_rules_version_code"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    product_version_id = Column(GUID(), ForeignKey("insurance_product_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(100), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    rule_type = Column(String(75), default="eligibility")
    decision_effect = Column(String(50), default="refer")
    condition = Column(JSON, default=dict)
    message = Column(String(500), nullable=True)
    authority_level = Column(String(75), nullable=True)
    priority = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company")
    product_version = relationship("ProductVersion", back_populates="underwriting_rules")


class QuoteWizardSchema(Base):
    """Versioned schema describing the customer/admin quote intake wizard."""

    __tablename__ = "product_quote_wizard_schemas"
    __table_args__ = (
        UniqueConstraint("product_version_id", "channel", "schema_version", name="uq_quote_wizard_schema_version_channel"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    product_version_id = Column(GUID(), ForeignKey("insurance_product_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    channel = Column(String(50), default="portal")
    schema_version = Column(String(50), default="1.0")
    title = Column(String(150), nullable=False)
    steps = Column(JSON, default=list)
    validation_schema = Column(JSON, default=dict)
    ui_schema = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company")
    product_version = relationship("ProductVersion", back_populates="wizard_schemas")
