from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.production_launch_control import (
    ApprovalDecision,
    ApprovalRequest,
    ConsequentialActionPolicy,
    DocumentTemplateApproval,
    LaunchReadinessCheck,
    ProductionAuditEvent,
)
from app.services.ai_action_control_service import AiActionControlService, RestrictedInsuranceOperation
from app.services.production_launch_control_service import (
    ActorContext,
    DocumentReleaseService,
    EnvironmentReadinessService,
    LaunchChecklistService,
    ProductionActionBlockedError,
    ProductionActionControlService,
)


LAUNCH_CONTROL_TABLES = [
    ConsequentialActionPolicy.__table__,
    ApprovalRequest.__table__,
    ApprovalDecision.__table__,
    ProductionAuditEvent.__table__,
    DocumentTemplateApproval.__table__,
    LaunchReadinessCheck.__table__,
]


@pytest.fixture
def launch_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    for table in LAUNCH_CONTROL_TABLES:
        table.create(engine, checkfirst=True)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        for table in reversed(LAUNCH_CONTROL_TABLES):
            table.drop(engine, checkfirst=True)
        engine.dispose()


def test_non_production_action_is_allowed_but_audited(launch_session):
    service = ProductionActionControlService(launch_session)
    company_id = uuid4()
    actor_id = uuid4()

    decision = service.evaluate_action(
        action_key="create_claim_record",
        actor=ActorContext(actor_id=actor_id, company_id=company_id, roles=("support_agent",)),
        company_id=company_id,
        target_type="claim",
        target_id=uuid4(),
        payload={"source": "unit_test"},
        environment="staging",
        correlation_id="plc-staging-1",
    )

    assert decision.allowed is True
    assert decision.requires_approval is False
    event = launch_session.query(ProductionAuditEvent).filter_by(correlation_id="plc-staging-1").one()
    assert event.decision == "allowed"
    assert event.action_key == "create_claim_record"
    assert event.event_metadata == {"payload_keys": ["source"]}


def test_production_blocks_unauthorized_actor_and_ai_direct_execution(launch_session):
    service = ProductionActionControlService(launch_session)
    company_id = uuid4()

    unauthorized = service.evaluate_action(
        action_key="take_payment",
        actor=ActorContext(actor_id=uuid4(), company_id=company_id, roles=("client",)),
        company_id=company_id,
        target_type="payment",
        target_id=uuid4(),
        payment_live_mode=True,
        environment="production",
    )
    assert unauthorized.allowed is False
    assert "required role" in unauthorized.reason

    blocked_ai = service.evaluate_action(
        action_key="take_payment",
        actor=ActorContext(actor_id=uuid4(), company_id=company_id, roles=("admin",), is_ai_actor=True),
        company_id=company_id,
        target_type="payment",
        target_id=uuid4(),
        payment_live_mode=True,
        environment="production",
    )
    assert blocked_ai.allowed is False
    assert "AI actors cannot directly execute" in blocked_ai.reason

    ai_decision = AiActionControlService().evaluate_operation(RestrictedInsuranceOperation.TAKE_PAYMENT)
    assert ai_decision.allowed is False
    assert ai_decision.deterministic_handoff_required is True


def test_approval_workflow_allows_and_consumes_production_policy_binding(launch_session):
    service = ProductionActionControlService(launch_session)
    document_service = DocumentReleaseService(launch_session)
    company_id = uuid4()
    actor_id = uuid4()
    policy_id = uuid4()

    document_service.approve_template(
        template_key="policy_certificate",
        version="1.0",
        jurisdiction="default",
        approved_by_id=actor_id,
        content_hash="hash-policy-certificate-v1",
    )
    request = service.request_approval(
        action_key="bind_policy",
        company_id=company_id,
        target_type="policy",
        target_id=policy_id,
        requested_by_id=actor_id,
        reason="Bind validated quote into policy.",
    )
    pending = service.evaluate_action(
        action_key="bind_policy",
        actor=ActorContext(actor_id=actor_id, company_id=company_id, roles=("underwriter",)),
        company_id=company_id,
        target_type="policy",
        target_id=policy_id,
        template_key="policy_certificate",
        approval_request_id=request.id,
        environment="production",
    )
    assert pending.allowed is False
    assert pending.requires_approval is True

    approval_decision = service.decide_approval(
        approval_request_id=request.id,
        decided_by_id=actor_id,
        decision="approved",
        decision_reason="Controls reviewed.",
    )
    assert approval_decision.decision == "approved"

    allowed = service.evaluate_action(
        action_key="bind_policy",
        actor=ActorContext(actor_id=actor_id, company_id=company_id, roles=("underwriter",)),
        company_id=company_id,
        target_type="policy",
        target_id=policy_id,
        template_key="policy_certificate",
        approval_request_id=request.id,
        environment="production",
    )
    assert allowed.allowed is True

    consumed_request = launch_session.query(ApprovalRequest).filter_by(id=request.id).one()
    assert consumed_request.status == "executed"
    assert consumed_request.executed_at is not None


def test_document_release_requires_approved_template_in_production(launch_session):
    action_service = ProductionActionControlService(launch_session)
    document_service = DocumentReleaseService(launch_session)
    company_id = uuid4()
    actor = ActorContext(actor_id=uuid4(), company_id=company_id, roles=("compliance_reviewer",))
    policy_id = uuid4()

    with pytest.raises(ProductionActionBlockedError, match="template version is not approved"):
        document_service.enforce_document_release(
            action_service=action_service,
            actor=actor,
            company_id=company_id,
            policy_id=policy_id,
            template_key="policy_certificate",
            environment="production",
        )

    document_service.approve_template(
        template_key="policy_certificate",
        version="1.0",
        jurisdiction="default",
        approved_by_id=actor.actor_id,
    )
    decision = document_service.enforce_document_release(
        action_service=action_service,
        actor=actor,
        company_id=company_id,
        policy_id=policy_id,
        template_key="policy_certificate",
        environment="production",
    )
    assert decision.allowed is True


def test_audit_events_are_append_only(launch_session):
    service = ProductionActionControlService(launch_session)
    company_id = uuid4()
    event = service.record_audit_event(
        company_id=company_id,
        actor_id=uuid4(),
        action_key="take_payment",
        event_type="action_evaluated",
        target_type="payment",
        target_id=uuid4(),
        decision="blocked",
        reason="unit test",
        payload={"amount": "100.00"},
    )
    launch_session.commit()

    event.reason = "tampered"
    with pytest.raises(ValueError, match="append-only"):
        launch_session.commit()
    launch_session.rollback()

    stored = launch_session.query(ProductionAuditEvent).filter_by(id=event.id).one()
    launch_session.delete(stored)
    with pytest.raises(ValueError, match="append-only"):
        launch_session.commit()
    launch_session.rollback()


def test_launch_readiness_and_checklist_surface_blocking_failures(launch_session, monkeypatch):
    monkeypatch.setattr("app.services.production_launch_control_service.settings.SECRET_KEY", "", raising=False)
    monkeypatch.setattr("app.services.production_launch_control_service.settings.DATABASE_URL", "sqlite:///unit-test.db", raising=False)
    monkeypatch.setattr("app.services.production_launch_control_service.settings.ENABLE_DEV_ENDPOINTS", True, raising=False)

    checks = EnvironmentReadinessService(launch_session).evaluate("production")
    check_statuses = {check.check_key: check.status for check in checks}
    assert check_statuses["environment_mode"] == "pass"
    assert check_statuses["dev_endpoints_disabled"] == "fail"
    assert check_statuses["required_runtime_settings"] == "fail"

    result = LaunchChecklistService(launch_session).evaluate("production")
    assert result.launch_allowed is False
    assert "dev_endpoints_disabled" in result.blocking_failures
    assert "required_runtime_settings" in result.blocking_failures
