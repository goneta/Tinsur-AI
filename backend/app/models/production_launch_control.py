"""Production Launch Control Layer models.

These models provide deterministic governance for legally and financially
consequential insurance operations. They intentionally attach control records to
existing tenant, user, policy, claim, payment, and document workflows instead of
making the core Quote, Policy, and Claim records product- or control-specific.
"""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, JSON, String, Text, UniqueConstraint, event
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.guid import GUID
from app.core.time import utcnow


class ConsequentialActionPolicy(Base):
    """Registry-backed policy defining how a restricted production action is controlled."""

    __tablename__ = "consequential_action_policies"
    __table_args__ = (
        UniqueConstraint("action_key", name="uq_consequential_action_policies_action_key"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    action_key = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    required_roles = Column(JSON, default=list, nullable=False)
    requires_approval = Column(Boolean, nullable=False, default=True, index=True)
    requires_document_template_approval = Column(Boolean, nullable=False, default=False)
    requires_payment_live_mode = Column(Boolean, nullable=False, default=False)
    audit_required = Column(Boolean, nullable=False, default=True)
    enabled = Column(Boolean, nullable=False, default=True, index=True)
    production_only_rules = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    approval_requests = relationship("ApprovalRequest", back_populates="action_policy")


class ApprovalRequest(Base):
    """Approval workflow request for a consequential insurance operation."""

    __tablename__ = "approval_requests"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    action_policy_id = Column(GUID(), ForeignKey("consequential_action_policies.id", ondelete="RESTRICT"), nullable=True, index=True)
    action_key = Column(String(100), nullable=False, index=True)
    target_type = Column(String(100), nullable=False, index=True)
    target_id = Column(String(100), nullable=False, index=True)
    requested_by_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    reason = Column(Text, nullable=True)
    request_payload = Column(JSON, default=dict, nullable=False)
    required_roles = Column(JSON, default=list, nullable=False)
    expires_at = Column(DateTime, nullable=True, index=True)
    executed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company")
    action_policy = relationship("ConsequentialActionPolicy", back_populates="approval_requests")
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    decisions = relationship("ApprovalDecision", back_populates="approval_request", cascade="all, delete-orphan")

    def mark_executed(self) -> None:
        """Mark the approval as consumed by deterministic execution."""

        self.status = "executed"
        self.executed_at = utcnow()


class ApprovalDecision(Base):
    """Individual approval or rejection decision for an approval request."""

    __tablename__ = "approval_decisions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    approval_request_id = Column(GUID(), ForeignKey("approval_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    decided_by_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    decision = Column(String(50), nullable=False, index=True)
    decision_reason = Column(Text, nullable=True)
    decision_payload = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    approval_request = relationship("ApprovalRequest", back_populates="decisions")
    decided_by = relationship("User", foreign_keys=[decided_by_id])


class ProductionAuditEvent(Base):
    """Append-only audit record for deterministic consequential action decisions and execution."""

    __tablename__ = "production_audit_events"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    approval_request_id = Column(GUID(), ForeignKey("approval_requests.id", ondelete="SET NULL"), nullable=True, index=True)
    action_key = Column(String(100), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    target_type = Column(String(100), nullable=False, index=True)
    target_id = Column(String(100), nullable=False, index=True)
    decision = Column(String(50), nullable=False, index=True)
    reason = Column(Text, nullable=True)
    payload_hash = Column(String(128), nullable=True)
    before_hash = Column(String(128), nullable=True)
    after_hash = Column(String(128), nullable=True)
    correlation_id = Column(String(100), nullable=True, index=True)
    environment = Column(String(50), nullable=False, default="unknown", index=True)
    event_metadata = Column("event_metadata", JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=utcnow, index=True)

    company = relationship("Company")
    actor = relationship("User", foreign_keys=[actor_id])
    approval_request = relationship("ApprovalRequest")



@event.listens_for(ProductionAuditEvent, "before_update")
def _prevent_production_audit_event_update(mapper, connection, target):  # pragma: no cover - exercised via flush/commit
    raise ValueError("Production audit events are append-only and cannot be updated")


@event.listens_for(ProductionAuditEvent, "before_delete")
def _prevent_production_audit_event_delete(mapper, connection, target):  # pragma: no cover - exercised via flush/commit
    raise ValueError("Production audit events are append-only and cannot be deleted")


class DocumentTemplateApproval(Base):
    """Versioned approval record for legal document templates used in production issuance."""

    __tablename__ = "document_template_approvals"
    __table_args__ = (
        UniqueConstraint("template_key", "version", "jurisdiction", name="uq_document_template_approval_version"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    template_key = Column(String(100), nullable=False, index=True)
    version = Column(String(50), nullable=False, default="1.0", index=True)
    jurisdiction = Column(String(100), nullable=False, default="default", index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    approved_by_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)
    content_hash = Column(String(128), nullable=True, index=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    approved_by = relationship("User", foreign_keys=[approved_by_id])

    def approve(self, approved_by_id: uuid.UUID | None = None) -> None:
        """Mark this legal template version as production-approved."""

        self.status = "approved"
        if approved_by_id is not None:
            self.approved_by_id = approved_by_id
        self.approved_at = utcnow()


class LaunchReadinessCheck(Base):
    """Machine-readable evidence for production launch readiness gates."""

    __tablename__ = "launch_readiness_checks"
    __table_args__ = (
        UniqueConstraint("check_key", name="uq_launch_readiness_checks_check_key"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    check_key = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    severity = Column(String(50), nullable=False, default="blocking", index=True)
    details = Column(JSON, default=dict, nullable=False)
    last_checked_at = Column(DateTime, default=utcnow, index=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
