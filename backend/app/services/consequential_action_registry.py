"""Central registry for consequential production insurance actions.

The registry is deterministic and side-effect free. It defines the canonical set of
legally or financially consequential operations that must be governed by the
Production Launch Control Layer before execution in production.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConsequentialAction(str, Enum):
    """Canonical restricted production insurance action keys."""

    BIND_POLICY = "bind_policy"
    CANCEL_POLICY = "cancel_policy"
    TAKE_PAYMENT = "take_payment"
    ISSUE_DOCUMENT = "issue_document"
    APPROVE_CLAIM = "approve_claim"
    SETTLE_CLAIM = "settle_claim"
    WAIVE_FEE = "waive_fee"
    CHANGE_POLICY_RECORD = "change_policy_record"
    REFUND_PAYMENT = "refund_payment"
    CREATE_CLAIM_RECORD = "create_claim_record"


@dataclass(frozen=True)
class ConsequentialActionDefinition:
    """Deterministic control definition for a restricted insurance action."""

    action_key: str
    description: str
    required_roles: tuple[str, ...]
    requires_approval: bool = True
    audit_required: bool = True
    requires_document_template_approval: bool = False
    requires_payment_live_mode: bool = False
    production_only_rules: dict[str, Any] = field(default_factory=dict)

    def to_policy_defaults(self) -> dict[str, Any]:
        return {
            "action_key": self.action_key,
            "description": self.description,
            "required_roles": list(self.required_roles),
            "requires_approval": self.requires_approval,
            "audit_required": self.audit_required,
            "requires_document_template_approval": self.requires_document_template_approval,
            "requires_payment_live_mode": self.requires_payment_live_mode,
            "enabled": True,
            "production_only_rules": dict(self.production_only_rules),
        }


class ConsequentialActionRegistry:
    """Authoritative in-code registry for fail-closed launch controls."""

    _DEFINITIONS: dict[ConsequentialAction, ConsequentialActionDefinition] = {
        ConsequentialAction.BIND_POLICY: ConsequentialActionDefinition(
            action_key=ConsequentialAction.BIND_POLICY.value,
            description="Bind or activate a policy and create a legal insurance contract.",
            required_roles=("admin", "underwriter", "compliance_reviewer"),
            requires_approval=True,
            requires_document_template_approval=True,
            production_only_rules={"requires_approved_quote_snapshot": True, "requires_payment_readiness": True},
        ),
        ConsequentialAction.CANCEL_POLICY: ConsequentialActionDefinition(
            action_key=ConsequentialAction.CANCEL_POLICY.value,
            description="Cancel an active policy or materially alter coverage status.",
            required_roles=("admin", "underwriter", "support_manager", "compliance_reviewer"),
            requires_approval=True,
            requires_document_template_approval=True,
            production_only_rules={"requires_reason_code": True, "requires_effective_date_validation": True},
        ),
        ConsequentialAction.TAKE_PAYMENT: ConsequentialActionDefinition(
            action_key=ConsequentialAction.TAKE_PAYMENT.value,
            description="Capture, post, or settle a customer payment.",
            required_roles=("admin", "finance_operator"),
            requires_approval=False,
            requires_payment_live_mode=True,
            production_only_rules={"requires_idempotency_key": True, "payment_provider_must_be_live": True},
        ),
        ConsequentialAction.ISSUE_DOCUMENT: ConsequentialActionDefinition(
            action_key=ConsequentialAction.ISSUE_DOCUMENT.value,
            description="Issue a legal policy, cancellation, claim, renewal, or payment document.",
            required_roles=("admin", "underwriter", "claims_handler", "compliance_reviewer"),
            requires_approval=False,
            requires_document_template_approval=True,
            production_only_rules={"approved_template_version_required": True},
        ),
        ConsequentialAction.APPROVE_CLAIM: ConsequentialActionDefinition(
            action_key=ConsequentialAction.APPROVE_CLAIM.value,
            description="Approve claim liability, claim amount, or claim outcome.",
            required_roles=("admin", "claims_handler", "claims_manager"),
            requires_approval=True,
            production_only_rules={"requires_claim_authority_limit": True},
        ),
        ConsequentialAction.SETTLE_CLAIM: ConsequentialActionDefinition(
            action_key=ConsequentialAction.SETTLE_CLAIM.value,
            description="Settle or pay a claim with financial consequence.",
            required_roles=("admin", "claims_manager", "finance_operator"),
            requires_approval=True,
            requires_payment_live_mode=True,
            production_only_rules={"requires_settlement_snapshot": True},
        ),
        ConsequentialAction.WAIVE_FEE: ConsequentialActionDefinition(
            action_key=ConsequentialAction.WAIVE_FEE.value,
            description="Waive, discount, or forgive a fee or premium obligation.",
            required_roles=("admin", "finance_operator", "support_manager"),
            requires_approval=True,
            production_only_rules={"requires_waiver_reason": True},
        ),
        ConsequentialAction.CHANGE_POLICY_RECORD: ConsequentialActionDefinition(
            action_key=ConsequentialAction.CHANGE_POLICY_RECORD.value,
            description="Change a legal policy record after issuance.",
            required_roles=("admin", "underwriter", "compliance_reviewer"),
            requires_approval=True,
            production_only_rules={"requires_before_after_snapshot": True},
        ),
        ConsequentialAction.REFUND_PAYMENT: ConsequentialActionDefinition(
            action_key=ConsequentialAction.REFUND_PAYMENT.value,
            description="Refund a completed customer payment.",
            required_roles=("admin", "finance_operator"),
            requires_approval=True,
            requires_payment_live_mode=True,
            production_only_rules={"requires_refund_reason": True, "requires_provider_response_capture": True},
        ),
        ConsequentialAction.CREATE_CLAIM_RECORD: ConsequentialActionDefinition(
            action_key=ConsequentialAction.CREATE_CLAIM_RECORD.value,
            description="Create a formal legal/operational claim record.",
            required_roles=("admin", "claims_handler", "support_agent"),
            requires_approval=False,
            production_only_rules={"requires_policy_validation": True},
        ),
    }

    @classmethod
    def all_definitions(cls) -> tuple[ConsequentialActionDefinition, ...]:
        return tuple(cls._DEFINITIONS.values())

    @classmethod
    def get(cls, action_key: str | ConsequentialAction) -> ConsequentialActionDefinition:
        normalized = cls.normalize(action_key)
        if normalized not in cls._DEFINITIONS:
            raise KeyError(f"Unknown consequential action: {action_key}")
        return cls._DEFINITIONS[normalized]

    @classmethod
    def is_restricted(cls, action_key: str | ConsequentialAction) -> bool:
        try:
            normalized = cls.normalize(action_key)
        except ValueError:
            return False
        return normalized in cls._DEFINITIONS

    @staticmethod
    def normalize(action_key: str | ConsequentialAction) -> ConsequentialAction:
        if isinstance(action_key, ConsequentialAction):
            return action_key
        return ConsequentialAction(str(action_key).strip().lower())
