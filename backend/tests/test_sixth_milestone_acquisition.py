"""
Focused tests for Milestone 6 automatic product-catalog policy acquisition.
"""
from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.schemas.product_catalog import ProductPolicyAcquisitionRequest, ProductQuoteRequest
from app.services.product_policy_acquisition_service import ProductPolicyAcquisitionService


class _FakeDB:
    def __init__(self):
        self.added = []
        self.flushed = 0

    def add(self, obj):
        self.added.append(obj)

    def flush(self):
        self.flushed += 1
        for obj in self.added:
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()


def _approved_product_quote(**overrides):
    payload = {
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
        "decision": "approved",
        "decision_reasons": [],
        "coverage_breakdown": [
            {
                "coverage_code": "collision",
                "coverage_name": "Collision",
                "option_code": "enhanced",
                "limit_amount": Decimal("25000.00"),
                "premium_delta": Decimal("50.00"),
                "rate_multiplier": Decimal("1.15"),
            }
        ],
        "factor_breakdown": [],
        "underwriting_decisions": [],
        "taxes_and_fees": [],
        "wizard_schema": None,
    }
    payload.update(overrides)
    return payload


def _request(**overrides):
    payload = {
        "client_id": uuid4(),
        "policy_type_id": uuid4(),
        "quote_request": ProductQuoteRequest(
            product_code="CAR_STANDARD",
            applicant_data={"first_name": "Ava", "last_name": "Client"},
            risk_data={"vehicle": {"market_value": 20000}, "driver": {"age": 35}},
        ),
        "auto_issue_policy": False,
        "idempotency_key": "m6-acquire-001",
    }
    payload.update(overrides)
    return ProductPolicyAcquisitionRequest(**payload)


def test_milestone6_rejects_declined_catalog_quote_acquisition():
    request = _request()
    declined = _approved_product_quote(decision="declined", is_eligible=False)

    with pytest.raises(ValueError, match="Declined product quotes"):
        ProductPolicyAcquisitionService._validate_acquisition_decision(declined, request)


def test_milestone6_requires_manual_referral_permission_before_acquisition():
    request = _request(allow_referred_quote=False)
    referred = _approved_product_quote(decision="referred", referral_required=True, decision_reasons=["manual_review"])

    with pytest.raises(ValueError, match="requires referral"):
        ProductPolicyAcquisitionService._validate_acquisition_decision(referred, request)


def test_milestone6_persists_policy_ready_quote_details_from_catalog_result():
    db = _FakeDB()
    service = ProductPolicyAcquisitionService(db)
    request = _request()
    quote_result = _approved_product_quote()

    quote = service._create_quote(uuid4(), request, quote_result, uuid4())

    assert quote.quote_number.startswith("CAR_STAN-")
    assert quote.status == "accepted"
    assert quote.auto_generated is True
    assert quote.final_premium == Decimal("1320.00")
    assert quote.coverage_amount == Decimal("25000.00")
    assert quote.details["product_catalog_acquisition"]["idempotency_key"] == "m6-acquire-001"
    assert quote.details["product_quote_result"]["estimated_premium"] == "1320.00"


def test_milestone6_underwriting_snapshot_is_policy_ready_for_existing_policy_service():
    db = _FakeDB()
    service = ProductPolicyAcquisitionService(db)
    company_id = uuid4()
    request = _request()
    quote_result = _approved_product_quote()
    quote = service._create_quote(company_id, request, quote_result, uuid4())
    decision = service._create_underwriting_decision(company_id, quote, request, quote_result)
    snapshot = service._create_snapshot(company_id, quote, decision, request, quote_result)

    assert decision.decision == "approve"
    assert decision.final_premium == Decimal("1320.00")
    assert snapshot.decision_snapshot["decision"] == "approve"
    assert snapshot.policy_ready_payload["product_code"] == "CAR_STANDARD"
    assert snapshot.policy_ready_payload["required_documents"] == [
        "identity_verification",
        "proof_of_address",
        "vehicle_registration",
        "driving_licence",
    ]


def test_milestone6_response_reports_existing_policy_idempotently():
    quote = SimpleNamespace(id=uuid4(), quote_number="CAR-123", status="policy_created")
    policy = SimpleNamespace(id=uuid4(), policy_number="POL-123", status="active")
    response = ProductPolicyAcquisitionService._build_response(quote, _approved_product_quote(), policy, idempotent=True)

    assert response["status"] == "policy_issued"
    assert response["policy_number"] == "POL-123"
    assert response["idempotent"] is True
