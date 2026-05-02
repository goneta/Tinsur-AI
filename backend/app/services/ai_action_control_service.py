"""AI action-control policy for production insurance automation.

Milestone intent: AI may recommend, explain, triage, and draft, but deterministic
application services must remain responsible for consequential insurance operations
such as binding policies, cancelling policies, taking payments, waiving fees,
settling claims, and changing legal policy records.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AiAssistanceMode(str, Enum):
    """Permitted AI assistance modes that do not mutate legal records."""

    RECOMMENDATION = "recommendation"
    EXPLANATION = "explanation"
    TRIAGE = "triage"
    DOCUMENT_DRAFT = "document_draft"
    READ_ONLY_LOOKUP = "read_only_lookup"
    ESCALATION_DRAFT = "escalation_draft"


class RestrictedInsuranceOperation(str, Enum):
    """Consequential operations that AI agents may not directly execute."""

    BIND_POLICY = "bind_policy"
    CANCEL_POLICY = "cancel_policy"
    TAKE_PAYMENT = "take_payment"
    REFUND_PAYMENT = "refund_payment"
    WAIVE_PAYMENT_OR_FEE = "waive_payment_or_fee"
    WAIVE_FEE = "waive_fee"
    CREATE_CLAIM_RECORD = "create_claim_record"
    APPROVE_CLAIM = "approve_claim"
    SETTLE_CLAIM = "settle_claim"
    ISSUE_DOCUMENT = "issue_document"
    CHANGE_LEGAL_POLICY_RECORD = "change_legal_policy_record"
    CHANGE_POLICY_RECORD = "change_policy_record"
    MUTATE_PRODUCT_CONFIGURATION = "mutate_product_configuration"


@dataclass(frozen=True)
class AiActionDecision:
    """Result of evaluating an AI-requested action."""

    operation: str
    allowed: bool
    reason: str
    deterministic_handoff_required: bool
    allowed_assistance: tuple[AiAssistanceMode, ...] = field(default_factory=tuple)
    handoff_target: str = "deterministic_service"

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "allowed": self.allowed,
            "reason": self.reason,
            "deterministic_handoff_required": self.deterministic_handoff_required,
            "allowed_assistance": [mode.value for mode in self.allowed_assistance],
            "handoff_target": self.handoff_target,
        }


class AiActionControlService:
    """Central guardrail for AI-exposed insurance action surfaces.

    The service is intentionally deterministic and side-effect free. It can be used by
    ADK tools, agent executors, API endpoints, and tests without requiring a database.
    """

    DEFAULT_ALLOWED_ASSISTANCE = (
        AiAssistanceMode.RECOMMENDATION,
        AiAssistanceMode.EXPLANATION,
        AiAssistanceMode.TRIAGE,
        AiAssistanceMode.DOCUMENT_DRAFT,
        AiAssistanceMode.ESCALATION_DRAFT,
    )

    _RESTRICTED_REASONS: dict[RestrictedInsuranceOperation, str] = {
        RestrictedInsuranceOperation.BIND_POLICY: (
            "Binding coverage creates or activates a legal insurance contract and must be executed by the deterministic policy service."
        ),
        RestrictedInsuranceOperation.CANCEL_POLICY: (
            "Cancelling coverage changes a legal policy record and must be executed by the deterministic policy lifecycle service."
        ),
        RestrictedInsuranceOperation.TAKE_PAYMENT: (
            "Taking or posting payment changes financial records and must be executed by the deterministic payment service."
        ),
        RestrictedInsuranceOperation.REFUND_PAYMENT: (
            "Refunding payment changes financial records and must be executed by deterministic payment controls with approval."
        ),
        RestrictedInsuranceOperation.WAIVE_PAYMENT_OR_FEE: (
            "Waiving fees changes financial obligations and must be executed by deterministic billing controls."
        ),
        RestrictedInsuranceOperation.WAIVE_FEE: (
            "Waiving fees changes financial obligations and must be executed by deterministic billing controls."
        ),
        RestrictedInsuranceOperation.CREATE_CLAIM_RECORD: (
            "Creating a claim is a legal/operational record change and must be submitted through deterministic claims intake."
        ),
        RestrictedInsuranceOperation.APPROVE_CLAIM: (
            "Approving claim liability or amount is a consequential claim decision and must be executed by deterministic claim services."
        ),
        RestrictedInsuranceOperation.SETTLE_CLAIM: (
            "Claim settlement can trigger financial and inter-company obligations and must be executed by deterministic claim services."
        ),
        RestrictedInsuranceOperation.ISSUE_DOCUMENT: (
            "Issuing legal documents requires approved templates and deterministic document-release controls."
        ),
        RestrictedInsuranceOperation.CHANGE_LEGAL_POLICY_RECORD: (
            "Legal policy record changes require deterministic validation, auditability, and authorization."
        ),
        RestrictedInsuranceOperation.CHANGE_POLICY_RECORD: (
            "Legal policy record changes require deterministic validation, auditability, and authorization."
        ),
        RestrictedInsuranceOperation.MUTATE_PRODUCT_CONFIGURATION: (
            "Product configuration changes affect rating and eligibility rules and must be executed by deterministic admin services."
        ),
    }

    def evaluate_operation(self, operation: str | RestrictedInsuranceOperation) -> AiActionDecision:
        """Return whether an AI layer may directly execute the requested operation."""

        normalized = self._normalize_operation(operation)
        if normalized in self._RESTRICTED_REASONS:
            return AiActionDecision(
                operation=normalized.value,
                allowed=False,
                reason=self._RESTRICTED_REASONS[normalized],
                deterministic_handoff_required=True,
                allowed_assistance=self.DEFAULT_ALLOWED_ASSISTANCE,
                handoff_target=self._handoff_target_for(normalized),
            )

        return AiActionDecision(
            operation=str(operation),
            allowed=True,
            reason="The requested operation is assistive or read-only and may be handled by the AI layer.",
            deterministic_handoff_required=False,
            allowed_assistance=(AiAssistanceMode.READ_ONLY_LOOKUP,),
            handoff_target="ai_layer",
        )

    def restricted_response(
        self,
        operation: str | RestrictedInsuranceOperation,
        *,
        requested_by: str = "ai_agent",
        record_reference: str | None = None,
        next_step: str | None = None,
    ) -> dict[str, Any]:
        """Build a standard blocked-action response for AI-exposed tools."""

        decision = self.evaluate_operation(operation)
        message = (
            "I can help explain options, prepare a draft, summarize risks, or route this to the correct workflow, "
            "but I cannot directly perform this consequential insurance action from the AI layer."
        )
        if next_step:
            message = f"{message} {next_step}"

        payload: dict[str, Any] = {
            "status": "blocked_ai_consequential_action",
            "requested_by": requested_by,
            "message": message,
            "decision": decision.to_dict(),
        }
        if record_reference:
            payload["record_reference"] = record_reference
        return payload

    def restricted_response_json(self, *args: Any, **kwargs: Any) -> str:
        """Return the blocked-action response as stable JSON for ADK tools."""

        return json.dumps(self.restricted_response(*args, **kwargs), sort_keys=True)

    @staticmethod
    def _normalize_operation(operation: str | RestrictedInsuranceOperation) -> RestrictedInsuranceOperation | str:
        if isinstance(operation, RestrictedInsuranceOperation):
            return operation
        try:
            return RestrictedInsuranceOperation(str(operation))
        except ValueError:
            return str(operation)

    @staticmethod
    def _handoff_target_for(operation: RestrictedInsuranceOperation) -> str:
        if operation in {RestrictedInsuranceOperation.BIND_POLICY, RestrictedInsuranceOperation.CANCEL_POLICY, RestrictedInsuranceOperation.CHANGE_LEGAL_POLICY_RECORD, RestrictedInsuranceOperation.CHANGE_POLICY_RECORD}:
            return "policy_lifecycle_service"
        if operation in {RestrictedInsuranceOperation.TAKE_PAYMENT, RestrictedInsuranceOperation.REFUND_PAYMENT, RestrictedInsuranceOperation.WAIVE_PAYMENT_OR_FEE, RestrictedInsuranceOperation.WAIVE_FEE}:
            return "payment_or_billing_service"
        if operation in {RestrictedInsuranceOperation.CREATE_CLAIM_RECORD, RestrictedInsuranceOperation.APPROVE_CLAIM, RestrictedInsuranceOperation.SETTLE_CLAIM}:
            return "claims_intake_or_settlement_service"
        if operation == RestrictedInsuranceOperation.ISSUE_DOCUMENT:
            return "document_release_service"
        if operation == RestrictedInsuranceOperation.MUTATE_PRODUCT_CONFIGURATION:
            return "product_admin_service"
        return "deterministic_service"


AI_CONSEQUENTIAL_ACTION_INSTRUCTIONS = """
AI ACTION CONTROL POLICY:
- You may recommend coverage, explain policy/payment/claim status, triage incidents, and draft documents or escalation notes.
- You must not directly bind/issue policies, cancel policies, take or post payments, refund payments, waive fees, create or approve claims, settle claims, issue legal documents, or change legal policy records.
- When a user asks for a consequential action, gather the minimum details needed, explain what will happen, and hand off to the deterministic service or a human-controlled workflow.
- Never tell the user that a restricted legal or financial action has been completed unless a deterministic service response explicitly confirms it.
""".strip()
