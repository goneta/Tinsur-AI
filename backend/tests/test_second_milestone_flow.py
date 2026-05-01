from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.time import utcnow
from app.services.payment_service import PaymentService
from app.services.quote_service import QuoteService


def _quote(final_premium="120.00"):
    return SimpleNamespace(
        id=uuid4(),
        company_id=uuid4(),
        final_premium=Decimal(final_premium),
    )


def _snapshot(quote, decision="approve", premium="120.00"):
    return SimpleNamespace(
        id=uuid4(),
        company_id=quote.company_id,
        valid_until=utcnow() + timedelta(days=1),
        decision_snapshot={"decision": decision, "final_premium": premium},
        policy_ready_payload={"decision": decision, "premium": premium, "required_documents": []},
        decision=None,
    )


def test_quote_validation_accepts_current_approved_underwriting_snapshot(monkeypatch):
    quote = _quote()
    service = object.__new__(QuoteService)
    snapshot = _snapshot(quote)

    monkeypatch.setattr(service, "get_underwriting_snapshot", lambda quote_id: snapshot)

    assert service.validate_policy_ready_underwriting(quote) is snapshot


def test_quote_validation_rejects_declined_underwriting_snapshot(monkeypatch):
    quote = _quote()
    service = object.__new__(QuoteService)
    snapshot = _snapshot(quote, decision="decline")

    monkeypatch.setattr(service, "get_underwriting_snapshot", lambda quote_id: snapshot)

    with pytest.raises(ValueError, match="underwriting decision"):
        service.validate_policy_ready_underwriting(quote)


def test_quote_validation_rejects_premium_mismatch(monkeypatch):
    quote = _quote(final_premium="120.00")
    service = object.__new__(QuoteService)
    snapshot = _snapshot(quote, premium="130.00")

    monkeypatch.setattr(service, "get_underwriting_snapshot", lambda quote_id: snapshot)

    with pytest.raises(ValueError, match="final premium"):
        service.validate_policy_ready_underwriting(quote)


def test_successful_policy_payment_side_effects_are_idempotent(monkeypatch):
    service = object.__new__(PaymentService)
    calls = []
    payment = SimpleNamespace(payment_metadata={})

    monkeypatch.setattr(service, "_generate_co_insurance_premium_shares", lambda payment: calls.append("co_insurance"))
    monkeypatch.setattr(service, "_generate_commissions", lambda payment: calls.append("commission"))
    monkeypatch.setattr(service, "_post_payment_to_ledger", lambda payment: calls.append("ledger"))

    service._handle_successful_policy_payment(payment)
    service._handle_successful_policy_payment(payment)

    assert calls == ["co_insurance", "commission", "ledger"]
    assert payment.payment_metadata["policy_payment_side_effects_completed"] is True
