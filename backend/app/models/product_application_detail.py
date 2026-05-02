"""
Product-specific detail attachment models for versioned insurance products.

These tables keep the core Quote, Policy, and Claim models generic while storing
validated, schema-versioned payloads that are specific to a product version.
Application detail records attach to quotes, rating snapshots attach to bound
policies, and claim detail records attach to claims.
"""
from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, JSON, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.guid import GUID
from app.core.time import utcnow


class ProductApplicationDetail(Base):
    """Versioned product-specific application data attached to a generic quote."""

    __tablename__ = "product_application_details"
    __table_args__ = (
        UniqueConstraint("quote_id", name="uq_product_application_details_quote_id"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    quote_id = Column(GUID(), ForeignKey("quotes.id", ondelete="CASCADE"), nullable=False, index=True)
    product_version_id = Column(GUID(), ForeignKey("insurance_product_versions.id", ondelete="RESTRICT"), nullable=False, index=True)
    quote_wizard_schema_id = Column(GUID(), ForeignKey("product_quote_wizard_schemas.id", ondelete="SET NULL"), nullable=True, index=True)
    schema_version = Column(String(50), nullable=False, default="1.0", index=True)
    validation_schema_ref = Column(String(255), nullable=True)
    application_data = Column(JSON, default=dict, nullable=False)
    validation_status = Column(String(50), nullable=False, default="pending", index=True)
    validation_errors = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company")
    quote = relationship("Quote", back_populates="product_application_detail")
    product_version = relationship("ProductVersion", back_populates="application_details")
    quote_wizard_schema = relationship("QuoteWizardSchema")

    def mark_validated(self) -> None:
        """Mark the application payload as validated."""

        self.validation_status = "valid"
        self.validation_errors = []

    def mark_invalid(self, errors: list[dict] | list[str]) -> None:
        """Mark the application payload as invalid with structured errors."""

        self.validation_status = "invalid"
        self.validation_errors = errors


class ProductRatingSnapshot(Base):
    """Versioned rating breakdown attached to a generic policy at bind time."""

    __tablename__ = "product_rating_snapshots"
    __table_args__ = (
        UniqueConstraint("policy_id", name="uq_product_rating_snapshots_policy_id"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    policy_id = Column(GUID(), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, index=True)
    product_version_id = Column(GUID(), ForeignKey("insurance_product_versions.id", ondelete="RESTRICT"), nullable=False, index=True)
    schema_version = Column(String(50), nullable=False, default="1.0", index=True)
    validation_schema_ref = Column(String(255), nullable=True)
    rating_data = Column(JSON, default=dict, nullable=False)
    validation_status = Column(String(50), nullable=False, default="pending", index=True)
    validation_errors = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company")
    policy = relationship("Policy", back_populates="product_rating_snapshot")
    product_version = relationship("ProductVersion", back_populates="rating_snapshots")

    def mark_validated(self) -> None:
        """Mark the rating payload as validated."""

        self.validation_status = "valid"
        self.validation_errors = []

    def mark_invalid(self, errors: list[dict] | list[str]) -> None:
        """Mark the rating payload as invalid with structured errors."""

        self.validation_status = "invalid"
        self.validation_errors = errors


class ProductClaimDetail(Base):
    """Versioned product-specific claim intake data attached to a generic claim."""

    __tablename__ = "product_claim_details"
    __table_args__ = (
        UniqueConstraint("claim_id", name="uq_product_claim_details_claim_id"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_id = Column(GUID(), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False, index=True)
    product_version_id = Column(GUID(), ForeignKey("insurance_product_versions.id", ondelete="RESTRICT"), nullable=False, index=True)
    schema_version = Column(String(50), nullable=False, default="1.0", index=True)
    validation_schema_ref = Column(String(255), nullable=True)
    claim_data = Column(JSON, default=dict, nullable=False)
    validation_status = Column(String(50), nullable=False, default="pending", index=True)
    validation_errors = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company")
    claim = relationship("Claim", back_populates="product_claim_detail")
    product_version = relationship("ProductVersion", back_populates="claim_details")

    def mark_validated(self) -> None:
        """Mark the claim-detail payload as validated."""

        self.validation_status = "valid"
        self.validation_errors = []

    def mark_invalid(self, errors: list[dict] | list[str]) -> None:
        """Mark the claim-detail payload as invalid with structured errors."""

        self.validation_status = "invalid"
        self.validation_errors = errors
