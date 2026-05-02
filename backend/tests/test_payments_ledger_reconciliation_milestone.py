"""
Focused tests for the payments, ledger, and reconciliation milestone.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from app.services.payment_ledger_reconciliation_service import PaymentLedgerReconciliationService


class _FakeQuery:
    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return None


class _FakeDb:
    def query(self, *args, **kwargs):
        return _FakeQuery()


class _FakePaymentRepository:
    def __init__(self, payments=None):
        self.payments = list(payments or [])
        self.updated = []

    def get_completed_payments_for_reconciliation(self, company_id, start_date, end_date):
        return [payment for payment in self.payments if payment.company_id == company_id]

    def get_transactions_by_payment(self, payment_id):
        return []

    def update(self, payment):
        self.updated.append(payment)
        return payment


class _FakeAccountingService:
    def __init__(self):
        self.initialized_companies = []
        self.posted_entries = []
        self.cash = SimpleNamespace(id=uuid4())
        self.revenue = SimpleNamespace(id=uuid4())

    def initialize_chart_of_accounts(self, company_id):
        self.initialized_companies.append(company_id)

    def get_or_create_account(self, company_id, code, name, account_type):
        return self.cash if code == "1000" else self.revenue

    def post_journal_entry(self, company_id, journal_data, creator_id):
        journal = SimpleNamespace(
            id=uuid4(),
            company_id=company_id,
            reference=journal_data.reference,
            entries=[
                SimpleNamespace(debit=entry.debit, credit=entry.credit)
                for entry in journal_data.entries
            ],
        )
        self.posted_entries.append((company_id, journal_data, creator_id, journal))
        return journal


def _payment(
    *,
    company_id=None,
    amount=Decimal("125.50"),
    status="completed",
    payment_method="cash",
    transactions=None,
    metadata=None,
):
    company_id = company_id or uuid4()
    return SimpleNamespace(
        id=uuid4(),
        company_id=company_id,
        policy_id=uuid4(),
        client_id=uuid4(),
        payment_number="PAY-REC-001",
        amount=amount,
        currency="XOF",
        payment_method=payment_method,
        payment_gateway=None,
        status=status,
        paid_at=datetime(2026, 5, 1, 10, 0, 0),
        created_at=datetime(2026, 5, 1, 9, 0, 0),
        created_by=uuid4(),
        payment_metadata=dict(metadata or {}),
        policy=SimpleNamespace(policy_number="POL-REC-001"),
        company=SimpleNamespace(admin_id=uuid4()),
        transactions=list(transactions or []),
    )


def _transaction(status="success", amount=Decimal("125.50")):
    return SimpleNamespace(
        id=uuid4(),
        transaction_id="GW-REC-001",
        status=status,
        amount=amount,
        initiated_at=datetime(2026, 5, 1, 10, 1, 0),
    )


def _journal(payment, amount=None, reference=None):
    amount = Decimal(str(amount if amount is not None else payment.amount))
    return SimpleNamespace(
        id=uuid4(),
        company_id=payment.company_id,
        reference=reference or f"PAYMENT:{payment.payment_number}",
        entries=[SimpleNamespace(debit=Decimal("0.00"), credit=amount)],
    )


class _InspectableReconciliationService(PaymentLedgerReconciliationService):
    def __init__(self, payments=None, existing_journals=None):
        self.repo = _FakePaymentRepository(payments)
        self.accounting = _FakeAccountingService()
        super().__init__(_FakeDb(), self.repo, self.accounting)
        self.existing_journals = dict(existing_journals or {})

    def _find_existing_payment_journal(self, payment):
        return self.existing_journals.get(payment.id)

    def _store_ledger_metadata(self, payment, journal_entry, ledger_status):
        super()._store_ledger_metadata(payment, journal_entry, ledger_status)
        self.existing_journals[payment.id] = journal_entry


def test_payment_ledger_posting_creates_balanced_idempotent_journal_metadata():
    payment = _payment()
    service = _InspectableReconciliationService([payment])

    packet = service.ensure_payment_posted_to_ledger(payment)

    assert packet["status"] == "posted"
    assert packet["ledger_amount"] == Decimal("125.50")
    assert service.accounting.initialized_companies == [payment.company_id]
    assert len(service.accounting.posted_entries) == 1
    _, journal_data, creator_id, journal = service.accounting.posted_entries[0]
    assert creator_id == payment.created_by
    assert journal_data.reference == f"PAYMENT:{payment.payment_number}"
    assert sum(entry.debit for entry in journal_data.entries) == Decimal("125.50")
    assert sum(entry.credit for entry in journal_data.entries) == Decimal("125.50")
    assert payment.payment_metadata["ledger_posting_status"] == "posted"
    assert payment.payment_metadata["ledger_journal_entry_id"] == str(journal.id)

    second_packet = service.ensure_payment_posted_to_ledger(payment)
    assert second_packet["status"] == "existing"
    assert len(service.accounting.posted_entries) == 1


def test_reconciliation_auto_posts_missing_ledger_and_marks_payment_reconciled():
    payment = _payment(transactions=[_transaction("success")])
    service = _InspectableReconciliationService([payment])

    result = service.reconcile_payments(
        payment.company_id,
        date(2026, 5, 1),
        date(2026, 5, 31),
        auto_post_missing=True,
        creator_id=payment.created_by,
    )

    assert result["total_payments"] == 1
    assert result["reconciled_payments"] == 1
    assert result["status_counts"]["ledger_posted"] == 1
    assert result["items"][0]["reconciliation_status"] == "ledger_posted"
    assert result["items"][0]["journal_entry_id"] is not None
    assert payment.payment_metadata["reconciliation_status"] == "ledger_posted"


def test_reconciliation_detects_ledger_amount_mismatch_without_reposting():
    payment = _payment(transactions=[_transaction("success")])
    journal = _journal(payment, amount=Decimal("99.00"))
    service = _InspectableReconciliationService([payment], {payment.id: journal})

    result = service.reconcile_payments(payment.company_id, date(2026, 5, 1), date(2026, 5, 31))

    item = result["items"][0]
    assert item["reconciliation_status"] == "amount_mismatch"
    assert item["ledger_amount"] == Decimal("99.00")
    assert result["unreconciled_payments"] == 1
    assert len(service.accounting.posted_entries) == 0


def test_reconciliation_flags_completed_payment_without_successful_gateway_transaction():
    payment = _payment(payment_method="mobile_money", transactions=[_transaction("pending")])
    journal = _journal(payment)
    service = _InspectableReconciliationService([payment], {payment.id: journal})

    result = service.reconcile_payments(payment.company_id, date(2026, 5, 1), date(2026, 5, 31))

    assert result["items"][0]["reconciliation_status"] == "gateway_pending"
    assert result["items"][0]["gateway_status"] == "pending"
    assert result["status_counts"]["gateway_pending"] == 1


def test_reconciliation_rejects_inverted_date_range():
    payment = _payment()
    service = _InspectableReconciliationService([payment])

    try:
        service.reconcile_payments(payment.company_id, date(2026, 6, 1), date(2026, 5, 1))
    except ValueError as exc:
        assert "end_date" in str(exc)
    else:
        raise AssertionError("Expected inverted reconciliation date range to fail")
