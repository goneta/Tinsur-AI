"""Pydantic schemas for Production Launch Control Layer records."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


ApprovalStatus = Literal["pending", "approved", "rejected", "expired", "executed"]
ApprovalDecisionValue = Literal["approved", "rejected"]
AuditDecision = Literal["allowed", "blocked", "requires_approval", "executed"]
ReadinessStatus = Literal["pending", "pass", "warning", "fail"]
TemplateApprovalStatus = Literal["pending", "approved", "rejected", "retired"]


class ConsequentialActionPolicyBase(BaseModel):
    action_key: str
    description: str
    required_roles: list[str] = Field(default_factory=list)
    requires_approval: bool = True
    requires_document_template_approval: bool = False
    requires_payment_live_mode: bool = False
    audit_required: bool = True
    enabled: bool = True
    production_only_rules: dict[str, Any] = Field(default_factory=dict)

    @field_validator("action_key")
    @classmethod
    def normalize_action_key(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("action_key is required")
        return normalized


class ConsequentialActionPolicyCreate(ConsequentialActionPolicyBase):
    pass


class ConsequentialActionPolicyUpdate(BaseModel):
    description: Optional[str] = None
    required_roles: Optional[list[str]] = None
    requires_approval: Optional[bool] = None
    requires_document_template_approval: Optional[bool] = None
    requires_payment_live_mode: Optional[bool] = None
    audit_required: Optional[bool] = None
    enabled: Optional[bool] = None
    production_only_rules: Optional[dict[str, Any]] = None


class ConsequentialActionPolicyResponse(ConsequentialActionPolicyBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ApprovalRequestBase(BaseModel):
    company_id: UUID
    action_key: str
    target_type: str
    target_id: str
    reason: Optional[str] = None
    request_payload: dict[str, Any] = Field(default_factory=dict)
    required_roles: list[str] = Field(default_factory=list)
    expires_at: Optional[datetime] = None

    @field_validator("action_key", "target_type", "target_id")
    @classmethod
    def require_non_empty_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("value must not be empty")
        return value.strip()


class ApprovalRequestCreate(ApprovalRequestBase):
    requested_by_id: Optional[UUID] = None
    action_policy_id: Optional[UUID] = None


class ApprovalRequestResponse(ApprovalRequestBase):
    id: UUID
    action_policy_id: Optional[UUID] = None
    requested_by_id: Optional[UUID] = None
    status: ApprovalStatus
    executed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ApprovalDecisionCreate(BaseModel):
    approval_request_id: UUID
    decided_by_id: Optional[UUID] = None
    decision: ApprovalDecisionValue
    decision_reason: Optional[str] = None
    decision_payload: dict[str, Any] = Field(default_factory=dict)


class ApprovalDecisionResponse(ApprovalDecisionCreate):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProductionAuditEventCreate(BaseModel):
    company_id: UUID
    actor_id: Optional[UUID] = None
    approval_request_id: Optional[UUID] = None
    action_key: str
    event_type: str
    target_type: str
    target_id: str
    decision: AuditDecision | str
    reason: Optional[str] = None
    payload_hash: Optional[str] = None
    before_hash: Optional[str] = None
    after_hash: Optional[str] = None
    correlation_id: Optional[str] = None
    environment: str = "unknown"
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProductionAuditEventResponse(ProductionAuditEventCreate):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DocumentTemplateApprovalBase(BaseModel):
    template_key: str
    version: str = "1.0"
    jurisdiction: str = "default"
    status: TemplateApprovalStatus = "pending"
    approval_notes: Optional[str] = None
    content_hash: Optional[str] = None

    @field_validator("template_key", "version", "jurisdiction")
    @classmethod
    def require_template_identity(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("template identity fields must not be empty")
        return value.strip()


class DocumentTemplateApprovalCreate(DocumentTemplateApprovalBase):
    approved_by_id: Optional[UUID] = None
    approved_at: Optional[datetime] = None


class DocumentTemplateApprovalResponse(DocumentTemplateApprovalBase):
    id: UUID
    approved_by_id: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LaunchReadinessCheckBase(BaseModel):
    check_key: str
    status: ReadinessStatus = "pending"
    severity: Literal["blocking", "warning", "informational"] = "blocking"
    details: dict[str, Any] = Field(default_factory=dict)

    @field_validator("check_key")
    @classmethod
    def require_check_key(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("check_key is required")
        return normalized


class LaunchReadinessCheckCreate(LaunchReadinessCheckBase):
    pass


class LaunchReadinessCheckResponse(LaunchReadinessCheckBase):
    id: UUID
    last_checked_at: datetime
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProductionActionDecision(BaseModel):
    action_key: str
    allowed: bool
    requires_approval: bool = False
    reason: str
    required_roles: list[str] = Field(default_factory=list)
    audit_required: bool = True
    approval_request_id: Optional[UUID] = None
    environment: str = "unknown"


class LaunchChecklistResult(BaseModel):
    launch_allowed: bool
    checks: list[LaunchReadinessCheckBase]
    blocking_failures: list[str] = Field(default_factory=list)
