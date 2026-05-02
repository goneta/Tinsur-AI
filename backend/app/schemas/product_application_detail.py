"""
Pydantic schemas for product-specific versioned detail attachments.

The core Quote, Policy, and Claim schemas remain generic. These DTOs represent
separate product-version attachments for quote application data, policy rating
snapshots, and claim intake details.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


ValidationStatus = Literal["pending", "valid", "invalid", "warning"]


class _ValidationFields(BaseModel):
    schema_version: str = "1.0"
    validation_schema_ref: Optional[str] = None
    validation_status: ValidationStatus = "pending"
    validation_errors: list[dict[str, Any] | str] = Field(default_factory=list)

    @field_validator("schema_version")
    @classmethod
    def require_schema_version(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("schema_version is required for product-specific records")
        return value.strip()

    @field_validator("validation_errors")
    @classmethod
    def require_errors_for_invalid_status(
        cls,
        value: list[dict[str, Any] | str],
        info,
    ) -> list[dict[str, Any] | str]:
        validation_status = info.data.get("validation_status")
        if validation_status == "invalid" and not value:
            raise ValueError("validation_errors are required when validation_status is invalid")
        return value


class ProductApplicationDetailBase(_ValidationFields):
    product_version_id: UUID
    quote_wizard_schema_id: Optional[UUID] = None
    application_data: dict[str, Any] = Field(default_factory=dict)

    @field_validator("application_data")
    @classmethod
    def require_application_payload(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("application_data must include the product-specific application payload")
        return value


class ProductApplicationDetailCreate(ProductApplicationDetailBase):
    quote_id: UUID
    company_id: UUID


class ProductApplicationDetailUpdate(_ValidationFields):
    product_version_id: Optional[UUID] = None
    quote_wizard_schema_id: Optional[UUID] = None
    application_data: Optional[dict[str, Any]] = None


class ProductApplicationDetailResponse(ProductApplicationDetailBase):
    id: UUID
    company_id: UUID
    quote_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProductRatingSnapshotBase(_ValidationFields):
    product_version_id: UUID
    rating_data: dict[str, Any] = Field(default_factory=dict)

    @field_validator("rating_data")
    @classmethod
    def require_rating_payload(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("rating_data must include the product-specific bind-time rating payload")
        return value


class ProductRatingSnapshotCreate(ProductRatingSnapshotBase):
    policy_id: UUID
    company_id: UUID


class ProductRatingSnapshotUpdate(_ValidationFields):
    product_version_id: Optional[UUID] = None
    rating_data: Optional[dict[str, Any]] = None


class ProductRatingSnapshotResponse(ProductRatingSnapshotBase):
    id: UUID
    company_id: UUID
    policy_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProductClaimDetailBase(_ValidationFields):
    product_version_id: UUID
    claim_data: dict[str, Any] = Field(default_factory=dict)

    @field_validator("claim_data")
    @classmethod
    def require_claim_payload(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("claim_data must include the product-specific claim intake payload")
        return value


class ProductClaimDetailCreate(ProductClaimDetailBase):
    claim_id: UUID
    company_id: UUID


class ProductClaimDetailUpdate(_ValidationFields):
    product_version_id: Optional[UUID] = None
    claim_data: Optional[dict[str, Any]] = None


class ProductClaimDetailResponse(ProductClaimDetailBase):
    id: UUID
    company_id: UUID
    claim_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
