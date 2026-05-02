"""
Milestone 8 premium schedule orchestration for product-catalog policy acquisition.

This service connects automatically issued product-catalog policies to the existing
premium schedule subsystem. It intentionally remains a thin orchestration layer:
it reuses PremiumService for installment generation and PremiumScheduleRepository
for idempotent lookup and summary calculation.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.policy import Policy
from app.models.premium_schedule import PremiumSchedule
from app.repositories.premium_schedule_repository import PremiumScheduleRepository
from app.services.premium_service import PremiumService


class ProductPolicyPremiumScheduleService:
    """Generate or reuse premium schedules for automatically issued policies."""

    def __init__(self, db: Session, schedule_repo: PremiumScheduleRepository | None = None):
        self.db = db
        self.schedule_repo = schedule_repo or PremiumScheduleRepository(db)
        self.premium_service = PremiumService(self.schedule_repo)

    def generate_schedule(
        self,
        company_id: UUID,
        policy: Policy,
        *,
        frequency: str,
        total_premium: Decimal,
        duration_months: int,
        start_date: date,
        grace_period_days: int = 15,
    ) -> dict[str, Any]:
        """Return an idempotent schedule packet for a tenant-owned policy."""
        if policy.company_id != company_id:
            raise ValueError("Cannot generate premium schedule for a policy outside the current tenant")

        existing = self.schedule_repo.get_by_policy(policy.id)
        if existing:
            return self._packet("existing", existing, frequency)

        schedules = self.premium_service.generate_payment_schedule(
            company_id=company_id,
            policy_id=policy.id,
            total_premium=Decimal(str(total_premium or 0)),
            frequency=frequency or "annual",
            start_date=start_date,
            duration_months=duration_months or 12,
            grace_period_days=grace_period_days,
        )
        return self._packet("generated", schedules, frequency)

    def _packet(self, status: str, schedules: list[PremiumSchedule], frequency: str) -> dict[str, Any]:
        return {
            "status": status,
            "schedule": [self._item(schedule) for schedule in schedules],
            "summary": self._summary(schedules, frequency),
            "generated_count": len(schedules) if status == "generated" else 0,
        }

    @staticmethod
    def _item(schedule: PremiumSchedule) -> dict[str, Any]:
        return {
            "schedule_id": schedule.id,
            "installment_number": schedule.installment_number,
            "due_date": schedule.due_date,
            "amount": Decimal(str(schedule.amount or 0)),
            "status": schedule.status,
            "grace_period_ends": schedule.grace_period_ends,
        }

    @staticmethod
    def _summary(schedules: list[PremiumSchedule], frequency: str) -> dict[str, Any]:
        total = sum((Decimal(str(schedule.amount or 0)) for schedule in schedules), Decimal("0"))
        paid = sum((Decimal(str(schedule.paid_amount or 0)) for schedule in schedules), Decimal("0"))
        return {
            "total_amount": total,
            "paid_amount": paid,
            "outstanding_amount": total - paid,
            "total_installments": len(schedules),
            "frequency": frequency,
        }
