import json
from pathlib import Path

from app.services.ai_action_control_service import (
    AI_CONSEQUENTIAL_ACTION_INSTRUCTIONS,
    AiActionControlService,
    RestrictedInsuranceOperation,
)


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def test_restricted_operations_require_deterministic_handoff():
    service = AiActionControlService()

    for operation in (
        RestrictedInsuranceOperation.BIND_POLICY,
        RestrictedInsuranceOperation.CANCEL_POLICY,
        RestrictedInsuranceOperation.TAKE_PAYMENT,
        RestrictedInsuranceOperation.WAIVE_PAYMENT_OR_FEE,
        RestrictedInsuranceOperation.CREATE_CLAIM_RECORD,
        RestrictedInsuranceOperation.SETTLE_CLAIM,
        RestrictedInsuranceOperation.CHANGE_LEGAL_POLICY_RECORD,
    ):
        decision = service.evaluate_operation(operation)

        assert decision.allowed is False
        assert decision.deterministic_handoff_required is True
        assert decision.handoff_target != "ai_layer"
        assert "document_draft" in decision.to_dict()["allowed_assistance"]
        assert "explanation" in decision.to_dict()["allowed_assistance"]


def test_assistive_or_read_only_operations_remain_allowed():
    service = AiActionControlService()

    decision = service.evaluate_operation("explain_policy_status")

    assert decision.allowed is True
    assert decision.deterministic_handoff_required is False
    assert decision.handoff_target == "ai_layer"
    assert decision.to_dict()["allowed_assistance"] == ["read_only_lookup"]


def test_restricted_response_json_is_stable_and_auditable():
    payload = json.loads(
        AiActionControlService().restricted_response_json(
            RestrictedInsuranceOperation.BIND_POLICY,
            requested_by="unit_test.policy_agent",
            record_reference="Q-123",
            next_step="Route to deterministic policy workflow.",
        )
    )

    assert payload["status"] == "blocked_ai_consequential_action"
    assert payload["requested_by"] == "unit_test.policy_agent"
    assert payload["record_reference"] == "Q-123"
    assert payload["decision"]["operation"] == "bind_policy"
    assert payload["decision"]["allowed"] is False
    assert payload["decision"]["handoff_target"] == "policy_lifecycle_service"
    assert "cannot directly perform" in payload["message"]
    assert "deterministic policy workflow" in payload["message"]


def test_agent_and_chat_prompts_include_consequential_action_policy():
    policy_executor = (BACKEND_ROOT / "agents/a2a_policy_agent/agent_executor.py").read_text()
    support_executor = (BACKEND_ROOT / "agents/a2a_support_agent/agent_executor.py").read_text()
    ai_service = (BACKEND_ROOT / "app/services/ai_service.py").read_text()

    for source in (policy_executor, support_executor, ai_service):
        assert "AI_CONSEQUENTIAL_ACTION_INSTRUCTIONS" in source

    assert "AI ACTION CONTROL POLICY" in AI_CONSEQUENTIAL_ACTION_INSTRUCTIONS
    assert "bind/issue policies" in AI_CONSEQUENTIAL_ACTION_INSTRUCTIONS
    assert "cancel policies" in AI_CONSEQUENTIAL_ACTION_INSTRUCTIONS
    assert "take or post payments" in AI_CONSEQUENTIAL_ACTION_INSTRUCTIONS
    assert "deterministic" in AI_CONSEQUENTIAL_ACTION_INSTRUCTIONS


def test_restricted_agent_tools_return_handoff_instead_of_mutating_records():
    policy_tools = (BACKEND_ROOT / "agents/a2a_policy_agent/tools.py").read_text()
    support_tools = (BACKEND_ROOT / "agents/a2a_support_agent/tools.py").read_text()
    claims_executor = (BACKEND_ROOT / "agents/a2a_claims_agent/agent_executor.py").read_text()

    assert "restricted_response_json" in policy_tools
    assert "policy_service.create_from_quote" not in policy_tools
    assert "policy.status = 'cancelled'" not in policy_tools
    assert "policy.status = 'canceled'" not in support_tools
    assert "schedule.status = 'waived'" not in support_tools
    assert "db.add(new_claim)" not in support_tools
    assert "Claim(" not in claims_executor
    assert "Settlement(" not in claims_executor
    assert "CREATE_CLAIM_RECORD" in claims_executor
    assert "SETTLE_CLAIM" in claims_executor
