"""Deterministic Production Launch Control Layer services.

This module centralizes fail-closed checks for legally and financially
consequential insurance operations. AI systems may propose actions, but this
service is the deterministic boundary that decides whether production execution
is allowed, blocked, or requires human approval.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterable
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.time import utcnow
from app.models.production_launch_control import (
    ApprovalDecision,
    ApprovalRequest,
    ConsequentialActionPolicy,
    DocumentTemplateApproval,
    LaunchReadinessCheck,
    ProductionAuditEvent,
)
from app.schemas.production_launch_control import LaunchChecklistResult, ProductionActionDecision
from app.services.consequential_action_registry import ConsequentialActionRegistry


PRODUCTION_ENVIRONMENTS = {"production", "prod", "live"}
NON_PRODUCTION_ENVIRONMENTS = {"development", "dev", "test", "testing", "local", "staging", "sandbox"}


class ProductionActionBlockedError(PermissionError):
    """Raised when a consequential action is not allowed to execute."""


@dataclass(frozen=True)
class ActorContext:
    """Minimal deterministic actor context for launch-control checks."""

    actor_id: UUID | None = None
    company_id: UUID | None = None
    roles: tuple[str, ...] = field(default_factory=tuple)
    is_ai_actor: bool = False

    @classmethod
    def from_user(cls, user: Any | None, *, roles: Iterable[str] | None = None, is_ai_actor: bool = False) -> "ActorContext":
        if user is None:
            return cls(roles=tuple(roles or ()), is_ai_actor=is_ai_actor)
        user_role = getattr(user, "role", None) or getattr(user, "user_type", None)
        merged_roles = list(roles or [])
        if user_role:
            merged_roles.append(str(user_role))
        return cls(
            actor_id=getattr(user, "id", None),
            company_id=getattr(user, "company_id", None),
            roles=tuple(sorted({str(role) for role in merged_roles if role})),
            is_ai_actor=is_ai_actor,
        )


def _environment_name(environment: str | None = None) -> str:
    return (environment or getattr(settings, "ENVIRONMENT", "development") or "development").strip().lower()


def _is_production(environment: str | None = None) -> bool:
    return _environment_name(environment) in PRODUCTION_ENVIRONMENTS


def _hash_payload(payload: Any) -> str:
    serialized = json.dumps(payload or {}, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class ProductionActionControlService:
    """Fail-closed control service for consequential production actions."""

    def __init__(self, db: Session):
        self.db = db

    def ensure_policy_seeded(self, action_key: str) -> ConsequentialActionPolicy:
        """Return a DB policy for an action, seeding from the registry if missing."""

        definition = ConsequentialActionRegistry.get(action_key)
        policy = (
            self.db.query(ConsequentialActionPolicy)
            .filter(ConsequentialActionPolicy.action_key == definition.action_key)
            .first()
        )
        if policy:
            return policy
        policy = ConsequentialActionPolicy(**definition.to_policy_defaults())
        self.db.add(policy)
        try:
            self.db.flush()
        except Exception:
            self.db.rollback()
            policy = (
                self.db.query(ConsequentialActionPolicy)
                .filter(ConsequentialActionPolicy.action_key == definition.action_key)
                .first()
            )
            if not policy:
                raise
        return policy

    def evaluate_action(
        self,
        *,
        action_key: str,
        actor: ActorContext | None = None,
        company_id: UUID | None = None,
        target_type: str,
        target_id: UUID | str,
        payload: dict[str, Any] | None = None,
        approval_request_id: UUID | None = None,
        template_key: str | None = None,
        template_version: str = "1.0",
        jurisdiction: str = "default",
        payment_live_mode: bool | None = None,
        environment: str | None = None,
        correlation_id: str | None = None,
        audit: bool = True,
    ) -> ProductionActionDecision:
        """Evaluate whether a consequential action may execute.

        Non-production environments remain permissive for developer velocity, but
        every production environment is fail-closed for unknown actions, missing
        roles, AI direct execution, missing approvals, missing legal template
        approvals, and payment-live-mode mismatches.
        """

        env = _environment_name(environment)
        actor = actor or ActorContext()
        company_id = company_id or actor.company_id
        payload = payload or {}

        try:
            policy = self.ensure_policy_seeded(action_key)
        except KeyError:
            return self._decision(
                action_key=action_key,
                allowed=False,
                requires_approval=False,
                reason="Unknown consequential action is blocked by default.",
                required_roles=[],
                audit_required=True,
                company_id=company_id,
                actor=actor,
                target_type=target_type,
                target_id=target_id,
                payload=payload,
                approval_request_id=approval_request_id,
                environment=env,
                correlation_id=correlation_id,
                audit=audit,
            )

        if not policy.enabled:
            return self._decision(
                action_key=policy.action_key,
                allowed=False,
                requires_approval=False,
                reason="Consequential action policy is disabled.",
                required_roles=policy.required_roles or [],
                audit_required=policy.audit_required,
                company_id=company_id,
                actor=actor,
                target_type=target_type,
                target_id=target_id,
                payload=payload,
                approval_request_id=approval_request_id,
                environment=env,
                correlation_id=correlation_id,
                audit=audit,
            )

        if not _is_production(env):
            return self._decision(
                action_key=policy.action_key,
                allowed=True,
                requires_approval=False,
                reason="Non-production environment: deterministic control logged without blocking developer/test execution.",
                required_roles=policy.required_roles or [],
                audit_required=policy.audit_required,
                company_id=company_id,
                actor=actor,
                target_type=target_type,
                target_id=target_id,
                payload=payload,
                approval_request_id=approval_request_id,
                environment=env,
                correlation_id=correlation_id,
                audit=audit,
            )

        if not company_id:
            return self._blocked(policy, actor, company_id, target_type, target_id, payload, approval_request_id, env, correlation_id, audit, "Company context is required for production consequential actions.")

        if actor.is_ai_actor:
            return self._blocked(policy, actor, company_id, target_type, target_id, payload, approval_request_id, env, correlation_id, audit, "AI actors cannot directly execute consequential production actions.")

        role_check = self._role_check(policy.required_roles or [], actor.roles)
        if not role_check:
            return self._blocked(policy, actor, company_id, target_type, target_id, payload, approval_request_id, env, correlation_id, audit, "Actor lacks a required role for this consequential action.")

        if policy.requires_payment_live_mode and payment_live_mode is not True:
            return self._blocked(policy, actor, company_id, target_type, target_id, payload, approval_request_id, env, correlation_id, audit, "Payment live mode is required for production payment consequences.")

        if policy.requires_document_template_approval:
            if not template_key:
                return self._blocked(policy, actor, company_id, target_type, target_id, payload, approval_request_id, env, correlation_id, audit, "Approved legal document template is required.")
            if not DocumentReleaseService(self.db).is_template_approved(template_key, template_version, jurisdiction):
                return self._blocked(policy, actor, company_id, target_type, target_id, payload, approval_request_id, env, correlation_id, audit, "Legal document template version is not approved for production release.")

        if policy.requires_approval:
            approval = self._load_valid_approval(approval_request_id, policy.action_key, company_id, target_type, str(target_id))
            if not approval:
                return self._decision(
                    action_key=policy.action_key,
                    allowed=False,
                    requires_approval=True,
                    reason="Human approval is required before production execution.",
                    required_roles=policy.required_roles or [],
                    audit_required=policy.audit_required,
                    company_id=company_id,
                    actor=actor,
                    target_type=target_type,
                    target_id=target_id,
                    payload=payload,
                    approval_request_id=approval_request_id,
                    environment=env,
                    correlation_id=correlation_id,
                    audit=audit,
                )
            approval.mark_executed()
            self.db.add(approval)

        return self._decision(
            action_key=policy.action_key,
            allowed=True,
            requires_approval=False,
            reason="Production launch-control checks passed.",
            required_roles=policy.required_roles or [],
            audit_required=policy.audit_required,
            company_id=company_id,
            actor=actor,
            target_type=target_type,
            target_id=target_id,
            payload=payload,
            approval_request_id=approval_request_id,
            environment=env,
            correlation_id=correlation_id,
            audit=audit,
        )

    def enforce_action(self, **kwargs: Any) -> ProductionActionDecision:
        """Evaluate an action and raise if blocked."""

        decision = self.evaluate_action(**kwargs)
        if not decision.allowed:
            raise ProductionActionBlockedError(decision.reason)
        return decision

    def request_approval(
        self,
        *,
        action_key: str,
        company_id: UUID,
        target_type: str,
        target_id: UUID | str,
        requested_by_id: UUID | None,
        reason: str | None = None,
        request_payload: dict[str, Any] | None = None,
        expires_at: datetime | None = None,
    ) -> ApprovalRequest:
        policy = self.ensure_policy_seeded(action_key)
        request = ApprovalRequest(
            company_id=company_id,
            action_policy_id=policy.id,
            action_key=policy.action_key,
            target_type=target_type,
            target_id=str(target_id),
            requested_by_id=requested_by_id,
            status="pending",
            reason=reason,
            request_payload=request_payload or {},
            required_roles=policy.required_roles or [],
            expires_at=expires_at,
        )
        self.db.add(request)
        self.db.flush()
        self.record_audit_event(
            company_id=company_id,
            actor_id=requested_by_id,
            approval_request_id=request.id,
            action_key=policy.action_key,
            event_type="approval_requested",
            target_type=target_type,
            target_id=target_id,
            decision="requires_approval",
            reason=reason,
            payload=request_payload or {},
        )
        return request

    def decide_approval(
        self,
        *,
        approval_request_id: UUID,
        decided_by_id: UUID | None,
        decision: str,
        decision_reason: str | None = None,
        decision_payload: dict[str, Any] | None = None,
    ) -> ApprovalDecision:
        request = self.db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_request_id).first()
        if not request:
            raise ValueError("Approval request not found")
        normalized = decision.strip().lower()
        if normalized not in {"approved", "rejected"}:
            raise ValueError("Approval decision must be approved or rejected")
        if request.status != "pending":
            raise ValueError("Only pending approval requests can be decided")

        approval_decision = ApprovalDecision(
            approval_request_id=request.id,
            decided_by_id=decided_by_id,
            decision=normalized,
            decision_reason=decision_reason,
            decision_payload=decision_payload or {},
        )
        request.status = normalized
        self.db.add(approval_decision)
        self.db.add(request)
        self.db.flush()
        self.record_audit_event(
            company_id=request.company_id,
            actor_id=decided_by_id,
            approval_request_id=request.id,
            action_key=request.action_key,
            event_type="approval_decided",
            target_type=request.target_type,
            target_id=request.target_id,
            decision=normalized,
            reason=decision_reason,
            payload=decision_payload or {},
        )
        return approval_decision

    def record_audit_event(
        self,
        *,
        company_id: UUID | None,
        actor_id: UUID | None = None,
        approval_request_id: UUID | None = None,
        action_key: str,
        event_type: str,
        target_type: str,
        target_id: UUID | str,
        decision: str,
        reason: str | None = None,
        payload: dict[str, Any] | None = None,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        environment: str | None = None,
    ) -> ProductionAuditEvent | None:
        if company_id is None:
            return None
        event = ProductionAuditEvent(
            company_id=company_id,
            actor_id=actor_id,
            approval_request_id=approval_request_id,
            action_key=action_key,
            event_type=event_type,
            target_type=target_type,
            target_id=str(target_id),
            decision=decision,
            reason=reason,
            payload_hash=_hash_payload(payload),
            before_hash=_hash_payload(before) if before is not None else None,
            after_hash=_hash_payload(after) if after is not None else None,
            correlation_id=correlation_id,
            environment=_environment_name(environment),
            event_metadata={"payload_keys": sorted((payload or {}).keys())},
        )
        self.db.add(event)
        self.db.flush()
        return event

    @staticmethod
    def _role_check(required_roles: Iterable[str], actor_roles: Iterable[str]) -> bool:
        required = {role for role in required_roles if role}
        actor = {role for role in actor_roles if role}
        if "super_admin" in actor:
            return True
        if not required:
            return bool(actor)
        return bool(required.intersection(actor))

    def _load_valid_approval(self, approval_request_id: UUID | None, action_key: str, company_id: UUID, target_type: str, target_id: str) -> ApprovalRequest | None:
        if not approval_request_id:
            return None
        approval = self.db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_request_id).first()
        if not approval:
            return None
        if approval.status != "approved":
            return None
        if approval.company_id != company_id or approval.action_key != action_key or approval.target_type != target_type or approval.target_id != str(target_id):
            return None
        if approval.expires_at and approval.expires_at < utcnow():
            approval.status = "expired"
            self.db.add(approval)
            return None
        return approval

    def _blocked(self, policy: ConsequentialActionPolicy, actor: ActorContext, company_id: UUID | None, target_type: str, target_id: UUID | str, payload: dict[str, Any], approval_request_id: UUID | None, environment: str, correlation_id: str | None, audit: bool, reason: str) -> ProductionActionDecision:
        return self._decision(
            action_key=policy.action_key,
            allowed=False,
            requires_approval=False,
            reason=reason,
            required_roles=policy.required_roles or [],
            audit_required=policy.audit_required,
            company_id=company_id,
            actor=actor,
            target_type=target_type,
            target_id=target_id,
            payload=payload,
            approval_request_id=approval_request_id,
            environment=environment,
            correlation_id=correlation_id,
            audit=audit,
        )

    def _decision(self, *, action_key: str, allowed: bool, requires_approval: bool, reason: str, required_roles: list[str], audit_required: bool, company_id: UUID | None, actor: ActorContext, target_type: str, target_id: UUID | str, payload: dict[str, Any], approval_request_id: UUID | None, environment: str, correlation_id: str | None, audit: bool) -> ProductionActionDecision:
        if audit and audit_required:
            self.record_audit_event(
                company_id=company_id,
                actor_id=actor.actor_id,
                approval_request_id=approval_request_id,
                action_key=action_key,
                event_type="action_evaluated",
                target_type=target_type,
                target_id=target_id,
                decision="allowed" if allowed else ("requires_approval" if requires_approval else "blocked"),
                reason=reason,
                payload=payload,
                correlation_id=correlation_id,
                environment=environment,
            )
        return ProductionActionDecision(
            action_key=action_key,
            allowed=allowed,
            requires_approval=requires_approval,
            reason=reason,
            required_roles=required_roles,
            audit_required=audit_required,
            approval_request_id=approval_request_id,
            environment=environment,
        )


class EnvironmentReadinessService:
    """Sanitized launch readiness checks for production execution."""

    REQUIRED_PRODUCTION_SETTINGS = ("SECRET_KEY", "DATABASE_URL")

    def __init__(self, db: Session):
        self.db = db

    def evaluate(self, environment: str | None = None) -> list[LaunchReadinessCheck]:
        env = _environment_name(environment)
        checks = [
            self._upsert_check(
                "environment_mode",
                "pass" if env in PRODUCTION_ENVIRONMENTS else "warning",
                "warning" if env not in PRODUCTION_ENVIRONMENTS else "blocking",
                {"environment": env, "production": env in PRODUCTION_ENVIRONMENTS},
            ),
            self._upsert_check(
                "dev_endpoints_disabled",
                "pass" if not getattr(settings, "ENABLE_DEV_ENDPOINTS", False) else "fail",
                "blocking",
                {"dev_endpoints_enabled": bool(getattr(settings, "ENABLE_DEV_ENDPOINTS", False))},
            ),
            self._upsert_check(
                "required_runtime_settings",
                "pass" if self._required_settings_present() else "fail",
                "blocking",
                {"checked": list(self.REQUIRED_PRODUCTION_SETTINGS)},
            ),
            self._upsert_check(
                "consequential_action_registry",
                "pass" if ConsequentialActionRegistry.all_definitions() else "fail",
                "blocking",
                {"action_count": len(ConsequentialActionRegistry.all_definitions())},
            ),
        ]
        self.db.flush()
        return checks

    def is_launch_ready(self, environment: str | None = None) -> bool:
        checks = self.evaluate(environment)
        return all(check.status != "fail" for check in checks if check.severity == "blocking")

    def _required_settings_present(self) -> bool:
        return all(bool(getattr(settings, key, None)) for key in self.REQUIRED_PRODUCTION_SETTINGS)

    def _upsert_check(self, check_key: str, status: str, severity: str, details: dict[str, Any]) -> LaunchReadinessCheck:
        check = self.db.query(LaunchReadinessCheck).filter(LaunchReadinessCheck.check_key == check_key).first()
        if not check:
            check = LaunchReadinessCheck(check_key=check_key)
        check.status = status
        check.severity = severity
        check.details = details
        check.last_checked_at = utcnow()
        self.db.add(check)
        return check


class DocumentReleaseService:
    """Legal template approval checks for document release."""

    def __init__(self, db: Session):
        self.db = db

    def is_template_approved(self, template_key: str, version: str = "1.0", jurisdiction: str = "default") -> bool:
        approval = (
            self.db.query(DocumentTemplateApproval)
            .filter(
                DocumentTemplateApproval.template_key == template_key,
                DocumentTemplateApproval.version == version,
                DocumentTemplateApproval.jurisdiction == jurisdiction,
                DocumentTemplateApproval.status == "approved",
            )
            .first()
        )
        return bool(approval)

    def approve_template(self, *, template_key: str, version: str = "1.0", jurisdiction: str = "default", approved_by_id: UUID | None = None, content_hash: str | None = None, approval_notes: str | None = None) -> DocumentTemplateApproval:
        approval = (
            self.db.query(DocumentTemplateApproval)
            .filter(
                DocumentTemplateApproval.template_key == template_key,
                DocumentTemplateApproval.version == version,
                DocumentTemplateApproval.jurisdiction == jurisdiction,
            )
            .first()
        )
        if not approval:
            approval = DocumentTemplateApproval(template_key=template_key, version=version, jurisdiction=jurisdiction)
        approval.status = "approved"
        approval.approved_by_id = approved_by_id
        approval.approved_at = utcnow()
        approval.content_hash = content_hash
        approval.approval_notes = approval_notes
        self.db.add(approval)
        self.db.flush()
        return approval

    def enforce_document_release(self, *, action_service: ProductionActionControlService, actor: ActorContext | None, company_id: UUID, policy_id: UUID | str, template_key: str, template_version: str = "1.0", jurisdiction: str = "default", environment: str | None = None) -> ProductionActionDecision:
        return action_service.enforce_action(
            action_key="issue_document",
            actor=actor,
            company_id=company_id,
            target_type="policy_document",
            target_id=policy_id,
            template_key=template_key,
            template_version=template_version,
            jurisdiction=jurisdiction,
            environment=environment,
        )


class LaunchChecklistService:
    """Aggregate launch readiness evidence into a single deterministic result."""

    def __init__(self, db: Session):
        self.db = db
        self.readiness = EnvironmentReadinessService(db)

    def evaluate(self, environment: str | None = None) -> LaunchChecklistResult:
        checks = self.readiness.evaluate(environment)
        blocking_failures = [check.check_key for check in checks if check.severity == "blocking" and check.status == "fail"]
        return LaunchChecklistResult(
            launch_allowed=not blocking_failures,
            checks=[
                {
                    "check_key": check.check_key,
                    "status": check.status,
                    "severity": check.severity,
                    "details": check.details or {},
                }
                for check in checks
            ],
            blocking_failures=blocking_failures,
        )
