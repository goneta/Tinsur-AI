"""
Focused tests for Milestone 9 initial payment orchestration during acquisition.
"""
from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from app.schemas.product_catalog import ProductPolicyAcquisitionRequest, ProductQuoteRequest
from app.services.product_policy_acquisition_service import ProductPolicyAcquisitionService
from app.services.product_policy_initial_payment_service import ProductPolicyInitialPaymentService


class _FakePaymentRepository:
    def __init__(self, existing=None, gateway_response=None):
        self.payments = list(existing or [])
        self.gateway_response = gateway_response or {"status": "success"}

    def get_by_policy(self, policy_id):
        return [payment for payment in self.payments if payment.policy_id == policy_id]

    def get_transactions_by_payment(self, payment_id):
        return [SimpleNamespace(gateway_response=self.gateway_response)]


class _FakePaymentService:
    def __init__(self, repo, created_status="completed"):
        self.repo = repo
        self.created_status = created_status
        self.create_calls = 0
        self.process_calls = 0

    def create_payment(self, **kwargs):
        self.create_calls += 1
        payment = SimpleNamespace(
            id=uuid4(),
            company_id=kwargs["company_id"],
            policy_id=kwargs["policy_id"],
            client_id=kwargs["client_id"],
            payment_number="PAY-M9-001",
            amount=kwargs["amount"],
            currency="XOF",
            payment_method=kwargs["payment_method"],
            payment_gateway=kwargs["payment_gateway"],
            status="pending",
            reference_number=None,
            failure_reason=None,
            payment_metadata=kwargs["metadata"],
        )
        self.repo.payments.append(payment)
        return payment

    def process_payment(self, payment_id, payment_details):
        self.process_calls += 1
        payment = next(payment for payment in self.repo.payments if payment.id == payment_id)
        payment.status = self.created_status
        payment.reference_number = payment_details.get("reference_number")
        return payment


class _FakeScheduleRepository:
    def __init__(self, schedule=None):
        self.schedule = schedule
        self.mark_calls = 0

    def get_pending_by_policy(self, policy_id):
        if self.schedule and self.schedule.policy_id == policy_id and self.schedule.status == "pending":
            return [self.schedule]
        return []

    def mark_as_paid(self, schedule_id, payment_id, amount):
        self.mark_calls += 1
        if self.schedule and self.schedule.id == schedule_id:
            self.schedule.status = "paid"
            self.schedule.payment_id = payment_id
            self.schedule.paid_amount = amount
            return self.schedule
        return None


class _FakeLoyaltyService:
    def __init__(self):
        self.calls = []

    def award_points(self, client_id, amount, reason):
        self.calls.append((client_id, amount, reason))


def _policy(company_id=None, client_id=None):
    return SimpleNamespace(
        id=uuid4(),
        company_id=company_id or uuid4(),
        client_id=client_id or uuid4(),
        policy_number="POL-M9-001",
        premium_amount=Decimal("1200.00"),
    )


def _schedule(policy, amount=Decimal("100.00")):
    return SimpleNamespace(
        id=uuid4(),
        company_id=policy.company_id,
        policy_id=policy.id,
        amount=amount,
        status="pending",
        payment_id=None,
        paid_amount=Decimal("0"),
    )


def _request(**overrides):
    payload = {
        "client_id": uuid4(),
        "quote_request": ProductQuoteRequest(
            product_code="CAR_STANDARD",
            applicant_data={"first_name": "Ava", "last_name": "Client"},
            risk_data={"vehicle": {"market_value": 20000}, "driver": {"age": 35}},
        ),
        "auto_issue_policy": True,
    }
    payload.update(overrides)
    return ProductPolicyAcquisitionRequest(**payload)


def _quote_result():
    return {
        "decision": "approved",
        "product_id": uuid4(),
        "product_code": "CAR_STANDARD",
        "product_name": "Car Standard",
        "product_line": "car",
        "product_version_id": uuid4(),
        "product_version": "2026.1",
        "currency": "USD",
        "term_months": 12,
        "rating_base": Decimal("20000.00"),
        "base_premium": Decimal("1000.00"),
        "subtotal_premium": Decimal("1200.00"),
        "taxes_and_fees_total": Decimal("120.00"),
        "estimated_premium": Decimal("1320.00"),
        "is_eligible": True,
        "referral_required": False,
        "decision_reasons": [],
        "coverage_breakdown": [],
        "factor_breakdown": [],
        "underwriting_decisions": [],
        "taxes_and_fees": [],
        "wizard_schema": None,
    }


def test_milestone9_acquisition_request_defaults_to_no_initial_payment():
    request = _request()

    assert request.initial_payment.collect_payment is False
    assert request.initial_payment.payment_details == {}
    assert request.initial_payment.settle_first_premium_schedule is True
    assert request.initial_payment.award_loyalty_points is True


def test_milestone9_initial_payment_uses_first_schedule_amount_and_settles_it():
    policy = _policy()
    schedule = _schedule(policy, amount=Decimal("100.00"))
    payment_repo = _FakePaymentRepository(gateway_response={"gateway": "cash", "status": "success"})
    schedule_repo = _FakeScheduleRepository(schedule)
    loyalty_service = _FakeLoyaltyService()
    service = ProductPolicyInitialPaymentService(
        db=SimpleNamespace(),
        payment_repo=payment_repo,
        schedule_repo=schedule_repo,
        loyalty_service=loyalty_service,
    )
    fake_payment_service = _FakePaymentService(payment_repo)
    service.payment_service = fake_payment_service

    packet = service.collect_initial_payment(
        policy.company_id,
        policy,
        payment_details={"method": "cash", "reference_number": "RCPT-100"},
        idempotency_key="acq-123",
    )

    assert packet["status"] == "processed"
    assert packet["payment"]["amount"] == Decimal("100.00")
    assert packet["payment"]["status"] == "completed"
    assert packet["schedule_settlement_status"] == "settled"
    assert packet["settled_schedule_id"] == schedule.id
    assert packet["loyalty_awarded"] is True
    assert fake_payment_service.create_calls == 1
    assert fake_payment_service.process_calls == 1
    assert schedule_repo.mark_calls == 1
    assert loyalty_service.calls[0][1] == Decimal("100.00")


def test_milestone9_initial_payment_reuses_existing_idempotent_payment():
    policy = _policy()
    existing_payment = SimpleNamespace(
        id=uuid4(),
        company_id=policy.company_id,
        policy_id=policy.id,
        client_id=policy.client_id,
        payment_number="PAY-M9-EXISTING",
        amount=Decimal("1200.00"),
        currency="XOF",
        payment_method="cash",
        payment_gateway=None,
        status="completed",
        reference_number="RCPT-EXISTING",
        failure_reason=None,
        payment_metadata={"source": "product_catalog_acquisition_initial_payment", "idempotency_key": "acq-123"},
    )
    payment_repo = _FakePaymentRepository(existing=[existing_payment])
    service = ProductPolicyInitialPaymentService(
        db=SimpleNamespace(),
        payment_repo=payment_repo,
        schedule_repo=_FakeScheduleRepository(),
        loyalty_service=_FakeLoyaltyService(),
    )
    fake_payment_service = _FakePaymentService(payment_repo)
    service.payment_service = fake_payment_service

    packet = service.collect_initial_payment(
        policy.company_id,
        policy,
        payment_details={"method": "cash"},
        idempotency_key="acq-123",
    )

    assert packet["status"] == "existing"
    assert packet["payment"]["payment_id"] == existing_payment.id
    assert fake_payment_service.create_calls == 0
    assert fake_payment_service.process_calls == 0


def test_milestone9_initial_payment_rejects_cross_tenant_policy():
    service = ProductPolicyInitialPaymentService(
        db=SimpleNamespace(),
        payment_repo=_FakePaymentRepository(),
        schedule_repo=_FakeScheduleRepository(),
    )

    try:
        service.collect_initial_payment(
            uuid4(),
            _policy(),
            payment_details={"method": "cash"},
        )
    except ValueError as exc:
        assert "tenant" in str(exc)
    else:
        raise AssertionError("Expected cross-tenant initial payment collection to fail")


def test_milestone9_acquisition_response_includes_initial_payment_metadata():
    quote = SimpleNamespace(id=uuid4(), quote_number="CAR-123", status="policy_created")
    policy = SimpleNamespace(id=uuid4(), policy_number="POL-123", status="active")
    payment_id = uuid4()
    schedule_id = uuid4()

    response = ProductPolicyAcquisitionService._build_response(
        quote,
        _quote_result(),
        policy,
        idempotent=False,
        document_packet={"status": "not_requested", "documents": []},
        schedule_packet={"status": "existing", "schedule": [], "summary": None},
        initial_payment_packet={
            "status": "processed",
            "payment": {
                "payment_id": payment_id,
                "payment_number": "PAY-M9-001",
                "amount": Decimal("100.00"),
                "currency": "XOF",
                "payment_method": "cash",
                "payment_gateway": None,
                "status": "completed",
                "reference_number": "RCPT-100",
                "failure_reason": None,
                "gateway_response": {"gateway": "cash", "status": "success"},
            },
            "schedule_settlement_status": "settled",
            "settled_schedule_id": schedule_id,
            "loyalty_awarded": True,
        },
    )

    assert response["status"] == "policy_issued"
    assert response["initial_payment_status"] == "processed"
    assert response["initial_payment"]["payment_id"] == payment_id
    assert response["initial_payment_schedule_settlement_status"] == "settled"
    assert response["initial_payment_settled_schedule_id"] == schedule_id
    assert response["initial_payment_loyalty_awarded"] is True


def test_milestone9_acquisition_can_skip_initial_payment_until_policy_exists():
    service = ProductPolicyAcquisitionService(SimpleNamespace())

    collect_request = _request(initial_payment={"collect_payment": True, "payment_details": {"method": "cash"}})
    skip_request = _request(initial_payment={"collect_payment": False})

    assert service._initial_payment_packet(uuid4(), None, collect_request)["status"] == "not_available"
    assert service._initial_payment_packet(uuid4(), _policy(), skip_request)["status"] == "not_requested"
