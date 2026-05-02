"""
Milestone 9 initial payment orchestration for product-catalog acquisition.

This service connects automatically issued product-catalog policies to the
existing payment subsystem. It deliberately stays as a thin acquisition-layer
orchestrator: payments are created and processed by PaymentService, the first
pending premium schedule is settled through PremiumScheduleRepository, and
loyalty awards use the existing LoyaltyService convention.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.models.policy import Policy
from app.models.premium_schedule import PremiumSchedule
from app.repositories.payment_repository import PaymentRepository
from app.repositories.premium_schedule_repository import PremiumScheduleRepository
from app.services.payment_service import PaymentService


class ProductPolicyInitialPaymentService:
    """Create, process, and summarize the first payment for an acquired policy."""

    def __init__(
        self,
        db: Session,
        payment_repo: PaymentRepository | None = None,
        schedule_repo: PremiumScheduleRepository | None = None,
        loyalty_service: Any | None = None,
    ):
        self.db = db
        self.payment_repo = payment_repo or PaymentRepository(db)
        self.schedule_repo = schedule_repo or PremiumScheduleRepository(db)
        self.payment_service = PaymentService(db, self.payment_repo)
        self.loyalty_service = loyalty_service

    def collect_initial_payment(
        self,
        company_id: UUID,
        policy: Policy,
        *,
        payment_details: dict[str, Any],
        amount: Optional[Decimal] = None,
        idempotency_key: Optional[str] = None,
        settle_first_schedule: bool = True,
        award_loyalty_points: bool = True,
    ) -> dict[str, Any]:
        """Return an idempotent initial-payment packet for a tenant-owned policy."""
        if policy.company_id != company_id:
            raise ValueError("Cannot collect an initial payment for a policy outside the current tenant")

        details = dict(payment_details or {})
        payment_method = details.get("method")
        if not payment_method:
            raise ValueError("Initial payment details must include a supported payment method")

        existing_payment = self._find_existing_initial_payment(company_id, policy.id, idempotency_key)
        if existing_payment:
            settled_schedule = self._settle_first_pending_schedule(policy, existing_payment) if existing_payment.status == "completed" and settle_first_schedule else None
            return self._packet("existing", existing_payment, settled_schedule)

        initial_amount = self._resolve_amount(policy, amount)
        metadata = {
            **details,
            "type": "policy_premium",
            "source": "product_catalog_acquisition_initial_payment",
            "idempotency_key": idempotency_key,
            "policy_number": getattr(policy, "policy_number", None),
        }
        payment = self.payment_service.create_payment(
            company_id=company_id,
            policy_id=policy.id,
            client_id=policy.client_id,
            amount=initial_amount,
            payment_method=payment_method,
            payment_gateway=details.get("gateway"),
            metadata=metadata,
        )
        processed_payment = self.payment_service.process_payment(
            payment.id,
            details,
            actor_id=getattr(policy, "created_by", None),
            actor_roles=("admin",),
            payment_live_mode=bool(details.get("live_mode")),
        )

        settled_schedule: PremiumSchedule | None = None
        loyalty_awarded = False
        if processed_payment.status == "completed":
            if settle_first_schedule:
                settled_schedule = self._settle_first_pending_schedule(policy, processed_payment)
            if award_loyalty_points:
                loyalty_awarded = self._award_loyalty_points(policy, processed_payment)

        packet = self._packet("processed", processed_payment, settled_schedule)
        packet["loyalty_awarded"] = loyalty_awarded
        return packet

    def _resolve_amount(self, policy: Policy, requested_amount: Optional[Decimal]) -> Decimal:
        if requested_amount is not None:
            return Decimal(str(requested_amount))

        pending = self.schedule_repo.get_pending_by_policy(policy.id)
        if pending:
            return Decimal(str(pending[0].amount or 0))
        return Decimal(str(getattr(policy, "premium_amount", 0) or 0))

    def _find_existing_initial_payment(
        self,
        company_id: UUID,
        policy_id: UUID,
        idempotency_key: Optional[str],
    ) -> Payment | None:
        if not idempotency_key:
            return None

        for payment in self.payment_repo.get_by_policy(policy_id):
            metadata = payment.payment_metadata or {}
            if (
                payment.company_id == company_id
                and metadata.get("source") == "product_catalog_acquisition_initial_payment"
                and metadata.get("idempotency_key") == idempotency_key
            ):
                return payment
        return None

    def _settle_first_pending_schedule(self, policy: Policy, payment: Payment) -> PremiumSchedule | None:
        pending = self.schedule_repo.get_pending_by_policy(policy.id)
        if not pending:
            return None
        return self.schedule_repo.mark_as_paid(pending[0].id, payment.id, Decimal(str(payment.amount or 0)))

    def _award_loyalty_points(self, policy: Policy, payment: Payment) -> bool:
        try:
            loyalty_service = self.loyalty_service
            if loyalty_service is None:
                from app.services.loyalty_service import LoyaltyService

                loyalty_service = LoyaltyService(self.db)
            loyalty_service.award_points(
                client_id=policy.client_id,
                amount=Decimal(str(payment.amount or 0)),
                reason=f"Initial payment for product-catalog policy {policy.policy_number}",
            )
            return True
        except Exception:
            return False

    def _latest_gateway_response(self, payment: Payment) -> dict[str, Any]:
        try:
            transactions = self.payment_repo.get_transactions_by_payment(payment.id)
        except Exception:
            return {}
        if not transactions:
            return {}
        return transactions[0].gateway_response or {}

    def _packet(self, status: str, payment: Payment, settled_schedule: PremiumSchedule | None) -> dict[str, Any]:
        gateway_response = self._latest_gateway_response(payment)
        return {
            "status": status,
            "payment": self._payment_item(payment, gateway_response),
            "schedule_settlement_status": "settled" if settled_schedule else "not_settled",
            "settled_schedule_id": settled_schedule.id if settled_schedule else None,
            "loyalty_awarded": False,
        }

    @staticmethod
    def _payment_item(payment: Payment, gateway_response: dict[str, Any]) -> dict[str, Any]:
        return {
            "payment_id": payment.id,
            "payment_number": payment.payment_number,
            "amount": Decimal(str(payment.amount or 0)),
            "currency": payment.currency,
            "payment_method": payment.payment_method,
            "payment_gateway": payment.payment_gateway,
            "status": payment.status,
            "reference_number": payment.reference_number,
            "failure_reason": payment.failure_reason,
            "gateway_response": gateway_response,
        }
