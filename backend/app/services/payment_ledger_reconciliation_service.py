"""
Payments, ledger, and reconciliation orchestration.

This service keeps payment settlement, double-entry ledger posting, and
operator reconciliation checks in one tenant-scoped boundary so every payment
entry point can reuse the same idempotent accounting behavior.
"""
from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.time import utcnow
from app.models.ledger import JournalEntry
from app.models.payment import Payment, PaymentTransaction
from app.repositories.payment_repository import PaymentRepository
from app.schemas.ledger import JournalEntryCreate, LedgerEntryCreate
from app.services.accounting_service import AccountingService


class PaymentLedgerReconciliationService:
    """Tenant-safe payment ledger posting and reconciliation service."""

    PAYMENT_LEDGER_SOURCE = "payment_ledger_reconciliation"

    def __init__(
        self,
        db: Session,
        payment_repo: Optional[PaymentRepository] = None,
        accounting_service: Optional[AccountingService] = None,
    ):
        self.db = db
        self.payment_repo = payment_repo or PaymentRepository(db)
        self.accounting_service = accounting_service or AccountingService(db)

    def ensure_payment_posted_to_ledger(
        self,
        payment: Payment,
        *,
        creator_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Create or reuse a balanced journal entry for a completed payment."""
        self._validate_completed_payment(payment)

        existing = self._find_existing_payment_journal(payment)
        if existing:
            self._store_ledger_metadata(payment, existing, "existing")
            return self._ledger_packet(payment, existing, "existing")

        self.accounting_service.initialize_chart_of_accounts(payment.company_id)
        cash_acc = self.accounting_service.get_or_create_account(payment.company_id, "1000", "Cash", "Asset")
        revenue_acc = self.accounting_service.get_or_create_account(
            payment.company_id,
            "4000",
            "Premium Income",
            "Revenue",
        )

        amount = self._decimal(payment.amount)
        description = "Payment received"
        if getattr(payment, "policy", None):
            description = f"Premium payment received for Policy {payment.policy.policy_number}"
        elif getattr(payment, "payment_number", None):
            description = f"Payment received for {payment.payment_number}"

        journal_data = JournalEntryCreate(
            description=description,
            reference=self._journal_reference(payment),
            entries=[
                LedgerEntryCreate(account_id=cash_acc.id, debit=amount, credit=Decimal("0.00")),
                LedgerEntryCreate(account_id=revenue_acc.id, debit=Decimal("0.00"), credit=amount),
            ],
        )

        creator_id = creator_id or self._resolve_creator_id(payment)
        if not creator_id:
            raise ValueError("A creator user is required to post payment ledger entries")

        journal_entry = self.accounting_service.post_journal_entry(
            payment.company_id,
            journal_data,
            creator_id,
        )
        self._store_ledger_metadata(payment, journal_entry, "posted")
        return self._ledger_packet(payment, journal_entry, "posted")

    def reconcile_payments(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date,
        *,
        auto_post_missing: bool = False,
        creator_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Reconcile completed payments against gateway transactions and ledger entries."""
        if end_date < start_date:
            raise ValueError("end_date must be on or after start_date")

        payments = self.payment_repo.get_completed_payments_for_reconciliation(
            company_id,
            start_date,
            end_date,
        )
        items: List[Dict[str, Any]] = []
        totals = {
            "matched": 0,
            "ledger_posted": 0,
            "missing_ledger": 0,
            "amount_mismatch": 0,
            "gateway_pending": 0,
            "errors": 0,
        }
        reconciled_total = Decimal("0.00")
        ledger_total = Decimal("0.00")

        for payment in payments:
            item = self._reconcile_payment(payment, auto_post_missing=auto_post_missing, creator_id=creator_id)
            items.append(item)
            totals[item["reconciliation_status"]] = totals.get(item["reconciliation_status"], 0) + 1
            if item["reconciliation_status"] in {"matched", "ledger_posted"}:
                reconciled_total += item["payment_amount"]
            ledger_total += item["ledger_amount"] or Decimal("0.00")

        return {
            "company_id": company_id,
            "start_date": start_date,
            "end_date": end_date,
            "auto_post_missing": auto_post_missing,
            "total_payments": len(payments),
            "reconciled_payments": totals["matched"] + totals["ledger_posted"],
            "reconciled_amount": reconciled_total,
            "ledger_amount": ledger_total,
            "unreconciled_payments": len(payments) - (totals["matched"] + totals["ledger_posted"]),
            "status_counts": totals,
            "items": items,
            "generated_at": utcnow(),
        }

    def _reconcile_payment(
        self,
        payment: Payment,
        *,
        auto_post_missing: bool,
        creator_id: Optional[UUID],
    ) -> Dict[str, Any]:
        journal_entry = self._find_existing_payment_journal(payment)
        ledger_amount = self._journal_credit_total(journal_entry) if journal_entry else Decimal("0.00")
        latest_transaction = self._latest_transaction(payment)
        gateway_status = self._gateway_status(payment, latest_transaction)
        payment_amount = self._decimal(payment.amount)
        notes: List[str] = []

        if gateway_status not in {"success", "completed"}:
            status = "gateway_pending"
            notes.append("No successful gateway transaction was found for this completed payment.")
        elif not journal_entry and auto_post_missing:
            try:
                packet = self.ensure_payment_posted_to_ledger(payment, creator_id=creator_id)
                journal_entry = packet["journal_entry"]
                ledger_amount = payment_amount
                status = "ledger_posted"
                notes.append("Missing payment journal entry was posted during reconciliation.")
            except Exception as exc:  # pragma: no cover - defensive branch exercised by operators
                status = "errors"
                notes.append(str(exc))
        elif not journal_entry:
            status = "missing_ledger"
            notes.append("Completed payment does not yet have a matching ledger journal entry.")
        elif ledger_amount != payment_amount:
            status = "amount_mismatch"
            notes.append("Ledger credit total does not match the payment amount.")
        else:
            status = "matched"
            notes.append("Payment, gateway transaction, and ledger entry are reconciled.")

        self._store_reconciliation_metadata(payment, status, journal_entry, latest_transaction, notes)
        return {
            "payment_id": payment.id,
            "payment_number": payment.payment_number,
            "policy_id": payment.policy_id,
            "client_id": payment.client_id,
            "payment_amount": payment_amount,
            "currency": payment.currency,
            "payment_status": payment.status,
            "gateway_transaction_id": getattr(latest_transaction, "transaction_id", None),
            "gateway_status": gateway_status,
            "journal_entry_id": getattr(journal_entry, "id", None),
            "journal_reference": getattr(journal_entry, "reference", None),
            "ledger_amount": ledger_amount,
            "reconciliation_status": status,
            "notes": notes,
        }

    def _validate_completed_payment(self, payment: Payment) -> None:
        if not payment:
            raise ValueError("Payment is required for ledger posting")
        if payment.status != "completed":
            raise ValueError("Only completed payments can be posted to the ledger")
        if not payment.company_id:
            raise ValueError("Payment must be tenant-scoped before ledger posting")
        if self._decimal(payment.amount) <= Decimal("0.00"):
            raise ValueError("Payment amount must be positive before ledger posting")

    def _find_existing_payment_journal(self, payment: Payment) -> Optional[JournalEntry]:
        metadata = payment.payment_metadata or {}
        journal_id = metadata.get("ledger_journal_entry_id")
        query = self.db.query(JournalEntry).filter(JournalEntry.company_id == payment.company_id)
        if journal_id:
            existing = query.filter(JournalEntry.id == journal_id).first()
            if existing:
                return existing
        references = [self._journal_reference(payment), payment.payment_number]
        return query.filter(JournalEntry.reference.in_(references)).first()

    def _journal_reference(self, payment: Payment) -> str:
        return f"PAYMENT:{payment.payment_number}"

    def _journal_credit_total(self, journal_entry: Optional[JournalEntry]) -> Decimal:
        if not journal_entry:
            return Decimal("0.00")
        return sum((self._decimal(entry.credit) for entry in journal_entry.entries), Decimal("0.00"))

    def _latest_transaction(self, payment: Payment) -> Optional[PaymentTransaction]:
        transactions = getattr(payment, "transactions", None)
        if transactions:
            return sorted(transactions, key=lambda txn: txn.initiated_at or datetime.min, reverse=True)[0]
        fetched = self.payment_repo.get_transactions_by_payment(payment.id)
        return fetched[0] if fetched else None

    def _gateway_status(self, payment: Payment, transaction: Optional[PaymentTransaction]) -> str:
        if transaction and transaction.status:
            return "completed" if transaction.status == "success" else transaction.status
        return "completed" if payment.status == "completed" and payment.payment_method == "cash" else "unknown"

    def _store_ledger_metadata(self, payment: Payment, journal_entry: JournalEntry, ledger_status: str) -> None:
        metadata = dict(payment.payment_metadata or {})
        metadata.update(
            {
                "ledger_posting_source": self.PAYMENT_LEDGER_SOURCE,
                "ledger_posting_status": ledger_status,
                "ledger_journal_entry_id": str(journal_entry.id),
                "ledger_journal_reference": journal_entry.reference,
                "ledger_posted_at": utcnow().isoformat(),
            }
        )
        payment.payment_metadata = metadata
        self.payment_repo.update(payment)

    def _store_reconciliation_metadata(
        self,
        payment: Payment,
        status: str,
        journal_entry: Optional[JournalEntry],
        transaction: Optional[PaymentTransaction],
        notes: Iterable[str],
    ) -> None:
        metadata = dict(payment.payment_metadata or {})
        metadata.update(
            {
                "reconciliation_status": status,
                "reconciled_at": utcnow().isoformat(),
                "reconciliation_notes": list(notes),
                "reconciliation_transaction_id": getattr(transaction, "transaction_id", None),
                "reconciliation_journal_entry_id": str(journal_entry.id) if journal_entry else None,
            }
        )
        payment.payment_metadata = metadata
        self.payment_repo.update(payment)

    def _ledger_packet(self, payment: Payment, journal_entry: JournalEntry, status: str) -> Dict[str, Any]:
        return {
            "status": status,
            "payment_id": payment.id,
            "payment_number": payment.payment_number,
            "journal_entry": journal_entry,
            "journal_entry_id": journal_entry.id,
            "journal_reference": journal_entry.reference,
            "ledger_amount": self._journal_credit_total(journal_entry),
        }

    def _resolve_creator_id(self, payment: Payment) -> Optional[UUID]:
        if getattr(payment, "created_by", None):
            return payment.created_by
        company = getattr(payment, "company", None)
        if company and getattr(company, "admin_id", None):
            return company.admin_id
        from app.models.user import User

        sys_user = self.db.query(User).filter(User.company_id == payment.company_id).first()
        return sys_user.id if sys_user else None

    def _decimal(self, value: Any) -> Decimal:
        return Decimal(str(value or "0.00")).quantize(Decimal("0.01"))
