"""
Focused tests for Milestone 8 automatic premium schedule orchestration.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from app.models.premium_schedule import PremiumSchedule
from app.schemas.product_catalog import ProductPolicyAcquisitionRequest, ProductQuoteRequest
from app.services.product_policy_acquisition_service import ProductPolicyAcquisitionService
from app.services.product_policy_premium_schedule_service import ProductPolicyPremiumScheduleService


class _FakeScheduleRepository:
    def __init__(self, existing=None):
        self.schedules = list(existing or [])
        self.create_bulk_calls = 0

    def get_by_policy(self, policy_id):
        return [schedule for schedule in self.schedules if schedule.policy_id == policy_id]

    def create_bulk(self, schedules):
        self.create_bulk_calls += 1
        for schedule in schedules:
            if schedule.id is None:
                schedule.id = uuid4()
        self.schedules.extend(schedules)
        return schedules


def _policy(company_id=None, client_id=None):
    return SimpleNamespace(
        id=uuid4(),
        company_id=company_id or uuid4(),
        client_id=client_id or uuid4(),
        policy_number="POL-M8-001",
        premium_amount=Decimal("1200.00"),
        premium_frequency="monthly",
        start_date=date(2026, 5, 1),
        end_date=date(2027, 5, 1),
        status="active",
    )


def _schedule(policy, installment="1 of 12", amount=Decimal("100.00"), paid_amount=None):
    return PremiumSchedule(
        id=uuid4(),
        company_id=policy.company_id,
        policy_id=policy.id,
        installment_number=installment,
        due_date=date(2026, 5, 1),
        amount=amount,
        status="pending",
        grace_period_days=Decimal("15"),
        grace_period_ends=date(2026, 5, 16),
        paid_amount=paid_amount,
    )


def _acquisition_request(**overrides):
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


def test_milestone8_acquisition_request_defaults_to_premium_schedule_generation():
    request = _acquisition_request()

    assert request.generate_premium_schedule is True
    assert request.premium_grace_period_days == 15


def test_milestone8_premium_schedule_generates_missing_installments():
    policy = _policy()
    repo = _FakeScheduleRepository()
    service = ProductPolicyPremiumScheduleService(db=SimpleNamespace(), schedule_repo=repo)

    packet = service.generate_schedule(
        policy.company_id,
        policy,
        frequency="monthly",
        total_premium=policy.premium_amount,
        duration_months=12,
        start_date=policy.start_date,
        grace_period_days=10,
    )

    assert packet["status"] == "generated"
    assert packet["generated_count"] == 12
    assert repo.create_bulk_calls == 1
    assert packet["summary"]["total_installments"] == 12
    assert packet["summary"]["total_amount"] == Decimal("1200.00")
    assert packet["schedule"][0]["installment_number"] == "1 of 12"
    assert packet["schedule"][0]["amount"] == Decimal("100.00")
    assert packet["schedule"][0]["grace_period_ends"] == date(2026, 5, 11)


def test_milestone8_premium_schedule_reuses_existing_installments_idempotently():
    policy = _policy()
    existing = _schedule(policy)
    repo = _FakeScheduleRepository(existing=[existing])
    service = ProductPolicyPremiumScheduleService(db=SimpleNamespace(), schedule_repo=repo)

    packet = service.generate_schedule(
        policy.company_id,
        policy,
        frequency="monthly",
        total_premium=policy.premium_amount,
        duration_months=12,
        start_date=policy.start_date,
    )

    assert packet["status"] == "existing"
    assert packet["generated_count"] == 0
    assert repo.create_bulk_calls == 0
    assert packet["schedule"] == [
        {
            "schedule_id": existing.id,
            "installment_number": "1 of 12",
            "due_date": date(2026, 5, 1),
            "amount": Decimal("100.00"),
            "status": "pending",
            "grace_period_ends": date(2026, 5, 16),
        }
    ]


def test_milestone8_premium_schedule_rejects_cross_tenant_policy():
    policy = _policy()
    service = ProductPolicyPremiumScheduleService(db=SimpleNamespace(), schedule_repo=_FakeScheduleRepository())

    try:
        service.generate_schedule(
            uuid4(),
            policy,
            frequency="annual",
            total_premium=policy.premium_amount,
            duration_months=12,
            start_date=policy.start_date,
        )
    except ValueError as exc:
        assert "tenant" in str(exc)
    else:
        raise AssertionError("Expected cross-tenant premium schedule generation to fail")


def test_milestone8_acquisition_response_includes_premium_schedule_metadata():
    quote = SimpleNamespace(id=uuid4(), quote_number="CAR-123", status="policy_created")
    policy = SimpleNamespace(id=uuid4(), policy_number="POL-123", status="active")
    schedule_id = uuid4()

    response = ProductPolicyAcquisitionService._build_response(
        quote,
        _quote_result(),
        policy,
        idempotent=False,
        document_packet={"status": "not_requested", "documents": []},
        schedule_packet={
            "status": "generated",
            "schedule": [
                {
                    "schedule_id": schedule_id,
                    "installment_number": "1 of 12",
                    "due_date": date(2026, 5, 1),
                    "amount": Decimal("100.00"),
                    "status": "pending",
                    "grace_period_ends": date(2026, 5, 16),
                }
            ],
            "summary": {
                "total_amount": Decimal("1200.00"),
                "paid_amount": Decimal("0"),
                "outstanding_amount": Decimal("1200.00"),
                "total_installments": 12,
                "frequency": "monthly",
            },
        },
    )

    assert response["status"] == "policy_issued"
    assert response["premium_schedule_status"] == "generated"
    assert response["premium_schedule"][0]["schedule_id"] == schedule_id
    assert response["premium_schedule_summary"]["total_installments"] == 12


def test_milestone8_acquisition_can_skip_schedule_generation_until_policy_exists():
    service = ProductPolicyAcquisitionService(SimpleNamespace())

    assert service._premium_schedule_packet(uuid4(), None, _acquisition_request())["status"] == "not_available"
    assert service._premium_schedule_packet(uuid4(), _policy(), _acquisition_request(generate_premium_schedule=False))["status"] == "not_requested"
