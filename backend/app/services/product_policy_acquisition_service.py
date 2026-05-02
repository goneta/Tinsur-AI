"""
Milestone 6 product policy acquisition orchestration.

This service bridges the Milestone 4 product catalog and Milestone 5 product quote
engine to the existing quote, underwriting snapshot, and policy issuance pipeline.
It enables a customer-facing flow where applicant and car/risk details can be
rated, persisted as a first-class quote, and optionally issued as an active policy
when the deterministic product decision is approved.
"""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core.time import utcnow
from app.models.policy import Policy
from app.models.quote import Quote
from app.models.underwriting import QuoteUnderwritingSnapshot, UnderwritingDecision
from app.repositories.endorsement_repository import EndorsementRepository
from app.repositories.policy_repository import PolicyRepository
from app.repositories.quote_repository import QuoteRepository
from app.schemas.product_catalog import ProductPolicyAcquisitionRequest
from app.services.policy_service import PolicyService
from app.services.product_policy_document_packet_service import ProductPolicyDocumentPacketService
from app.services.product_policy_premium_schedule_service import ProductPolicyPremiumScheduleService
from app.services.product_quote_engine_service import ProductQuoteEngineService


class ProductPolicyAcquisitionService:
    """Persist product-catalog quote decisions and optionally issue policies."""

    def __init__(self, db: Session):
        self.db = db
        self.quote_engine = ProductQuoteEngineService(db)

    def acquire_policy(
        self,
        company_id: UUID,
        request: ProductPolicyAcquisitionRequest,
        created_by: UUID,
    ) -> dict[str, Any]:
        """Create a policy-ready quote from a product quote request and optionally issue it."""
        quote_result = self.quote_engine.calculate_quote(company_id, request.quote_request)
        self._validate_acquisition_decision(quote_result, request)

        existing_quote = self._find_existing_quote(company_id, request)
        if existing_quote:
            policy = self._get_existing_policy(existing_quote.id)
            if request.auto_issue_policy and not policy and self._is_approved(quote_result):
                policy = self._issue_policy(existing_quote, request, created_by)
            document_packet = self._document_packet(company_id, policy, request)
            schedule_packet = self._premium_schedule_packet(company_id, policy, request)
            return self._build_response(existing_quote, quote_result, policy, idempotent=True, document_packet=document_packet, schedule_packet=schedule_packet)

        quote = self._create_quote(company_id, request, quote_result, created_by)
        decision = self._create_underwriting_decision(company_id, quote, request, quote_result)
        self._create_snapshot(company_id, quote, decision, request, quote_result)
        self.db.commit()
        self.db.refresh(quote)

        policy: Optional[Policy] = None
        if request.auto_issue_policy and self._is_approved(quote_result):
            policy = self._issue_policy(quote, request, created_by)

        document_packet = self._document_packet(company_id, policy, request)
        schedule_packet = self._premium_schedule_packet(company_id, policy, request)
        return self._build_response(quote, quote_result, policy, idempotent=False, document_packet=document_packet, schedule_packet=schedule_packet)

    @staticmethod
    def _validate_acquisition_decision(quote_result: dict[str, Any], request: ProductPolicyAcquisitionRequest) -> None:
        decision = quote_result.get("decision")
        if decision == "declined" or not quote_result.get("is_eligible"):
            raise ValueError("Declined product quotes cannot be acquired as policies")
        if quote_result.get("referral_required") and not request.allow_referred_quote:
            raise ValueError("This product quote requires referral before acquisition")
        if request.auto_issue_policy and not ProductPolicyAcquisitionService._is_approved(quote_result):
            raise ValueError("Only approved product quotes can be issued automatically")

    @staticmethod
    def _is_approved(quote_result: dict[str, Any]) -> bool:
        return quote_result.get("decision") in {"approved", "approve"} and not quote_result.get("referral_required")

    def _find_existing_quote(self, company_id: UUID, request: ProductPolicyAcquisitionRequest) -> Optional[Quote]:
        if not request.idempotency_key:
            return None
        candidates = (
            self.db.query(Quote)
            .filter(Quote.company_id == company_id, Quote.client_id == request.client_id)
            .order_by(Quote.created_at.desc())
            .limit(50)
            .all()
        )
        for quote in candidates:
            acquisition = (quote.details or {}).get("product_catalog_acquisition", {})
            if acquisition.get("idempotency_key") == request.idempotency_key:
                return quote
        return None

    def _create_quote(
        self,
        company_id: UUID,
        request: ProductPolicyAcquisitionRequest,
        quote_result: dict[str, Any],
        created_by: UUID,
    ) -> Quote:
        quote = Quote(
            company_id=company_id,
            client_id=request.client_id,
            policy_type_id=request.policy_type_id,
            quote_number=self._generate_quote_number(quote_result.get("product_code")),
            sale_channel=request.sale_channel,
            coverage_amount=self._coverage_amount(quote_result),
            premium_amount=quote_result["subtotal_premium"],
            tax_amount=quote_result.get("taxes_and_fees_total", Decimal("0")),
            final_premium=quote_result["estimated_premium"],
            premium_frequency=request.premium_frequency,
            duration_months=quote_result.get("term_months") or request.quote_request.term_months,
            risk_score=self._risk_score(quote_result),
            status="accepted" if self._is_approved(quote_result) else "under_review",
            valid_until=(utcnow() + timedelta(days=request.valid_for_days)).date(),
            valid_for_days=request.valid_for_days,
            auto_generated=True,
            details={
                "product_catalog_acquisition": self._jsonable({
                    "idempotency_key": request.idempotency_key,
                    "auto_issue_policy": request.auto_issue_policy,
                    "product_id": quote_result.get("product_id"),
                    "product_code": quote_result.get("product_code"),
                    "product_name": quote_result.get("product_name"),
                    "product_line": quote_result.get("product_line"),
                    "product_version_id": quote_result.get("product_version_id"),
                    "product_version": quote_result.get("product_version"),
                    "currency": quote_result.get("currency"),
                    "requested_start_date": request.requested_start_date,
                    "source": "product_catalog_quote_engine",
                }),
                "applicant_data": self._jsonable(request.quote_request.applicant_data),
                "risk_data": self._jsonable(request.quote_request.risk_data),
                "coverage_selections": self._jsonable([item.model_dump() for item in request.quote_request.coverage_selections]),
                "product_quote_result": self._jsonable(quote_result),
            },
            notes=request.notes,
            created_by=created_by,
        )
        self.db.add(quote)
        self.db.flush()
        return quote

    def _create_underwriting_decision(
        self,
        company_id: UUID,
        quote: Quote,
        request: ProductPolicyAcquisitionRequest,
        quote_result: dict[str, Any],
    ) -> UnderwritingDecision:
        mapped_decision = self._mapped_decision(quote_result.get("decision"))
        decision = UnderwritingDecision(
            company_id=company_id,
            quote_id=quote.id,
            decision=mapped_decision,
            status="final" if mapped_decision == "approve" else "pending_referral",
            base_premium=quote_result.get("base_premium", Decimal("0")),
            final_premium=quote_result.get("estimated_premium", Decimal("0")),
            risk_score=quote.risk_score or Decimal("0"),
            breakdown=self._jsonable({
                "rating_base": quote_result.get("rating_base"),
                "coverage_breakdown": quote_result.get("coverage_breakdown", []),
                "factor_breakdown": quote_result.get("factor_breakdown", []),
                "taxes_and_fees": quote_result.get("taxes_and_fees", []),
            }),
            referral_reasons=self._jsonable(quote_result.get("decision_reasons", [])) if mapped_decision == "refer" else [],
            decline_reasons=self._jsonable(quote_result.get("decision_reasons", [])) if mapped_decision == "decline" else [],
            required_documents=self._required_documents(quote_result),
            warnings=[],
            assumptions=["Product catalog quote result persisted as the policy-ready underwriting snapshot."],
            rule_matches=self._jsonable(quote_result.get("underwriting_decisions", [])),
            input_snapshot=self._jsonable({
                "applicant_data": request.quote_request.applicant_data,
                "risk_data": request.quote_request.risk_data,
                "coverage_selections": [item.model_dump() for item in request.quote_request.coverage_selections],
            }),
        )
        self.db.add(decision)
        self.db.flush()
        return decision

    def _create_snapshot(
        self,
        company_id: UUID,
        quote: Quote,
        decision: UnderwritingDecision,
        request: ProductPolicyAcquisitionRequest,
        quote_result: dict[str, Any],
    ) -> QuoteUnderwritingSnapshot:
        snapshot = QuoteUnderwritingSnapshot(
            company_id=company_id,
            quote_id=quote.id,
            underwriting_decision_id=decision.id,
            normalized_payload=self._jsonable({
                "client_id": request.client_id,
                "applicant_data": request.quote_request.applicant_data,
                "risk_data": request.quote_request.risk_data,
                "coverage_selections": [item.model_dump() for item in request.quote_request.coverage_selections],
                "term_months": request.quote_request.term_months,
            }),
            decision_snapshot=self._jsonable({
                "decision": decision.decision,
                "source_decision": quote_result.get("decision"),
                "is_eligible": quote_result.get("is_eligible"),
                "referral_required": quote_result.get("referral_required"),
                "decision_reasons": quote_result.get("decision_reasons", []),
            }),
            premium_breakdown=self._jsonable({
                "currency": quote_result.get("currency"),
                "base_premium": quote_result.get("base_premium"),
                "subtotal_premium": quote_result.get("subtotal_premium"),
                "taxes_and_fees_total": quote_result.get("taxes_and_fees_total"),
                "estimated_premium": quote_result.get("estimated_premium"),
                "coverage_breakdown": quote_result.get("coverage_breakdown", []),
                "factor_breakdown": quote_result.get("factor_breakdown", []),
            }),
            policy_ready_payload=self._jsonable({
                "client_id": request.client_id,
                "policy_type_id": request.policy_type_id,
                "product_id": quote_result.get("product_id"),
                "product_code": quote_result.get("product_code"),
                "product_name": quote_result.get("product_name"),
                "product_line": quote_result.get("product_line"),
                "product_version_id": quote_result.get("product_version_id"),
                "coverage_amount": quote.coverage_amount,
                "final_premium": quote.final_premium,
                "premium_frequency": quote.premium_frequency,
                "duration_months": quote.duration_months,
                "requested_start_date": request.requested_start_date,
                "required_documents": self._required_documents(quote_result),
            }),
            valid_until=utcnow() + timedelta(days=request.valid_for_days),
        )
        self.db.add(snapshot)
        self.db.flush()
        return snapshot

    def _issue_policy(self, quote: Quote, request: ProductPolicyAcquisitionRequest, created_by: UUID) -> Optional[Policy]:
        start_date = request.requested_start_date or date.today()
        policy_service = PolicyService(
            PolicyRepository(self.db),
            QuoteRepository(self.db),
            EndorsementRepository(self.db),
        )
        return policy_service.create_from_quote(quote.id, start_date, created_by)

    def _get_existing_policy(self, quote_id: UUID) -> Optional[Policy]:
        return self.db.query(Policy).filter(Policy.quote_id == quote_id).first()

    def _document_packet(
        self,
        company_id: UUID,
        policy: Optional[Policy],
        request: ProductPolicyAcquisitionRequest,
    ) -> dict[str, Any]:
        if not request.generate_policy_documents:
            return {"status": "not_requested", "documents": []}
        if not policy:
            return {"status": "not_available", "documents": []}
        return ProductPolicyDocumentPacketService(self.db).generate_packet(
            company_id,
            policy,
            regenerate=request.regenerate_policy_documents,
        )

    def _premium_schedule_packet(
        self,
        company_id: UUID,
        policy: Optional[Policy],
        request: ProductPolicyAcquisitionRequest,
    ) -> dict[str, Any]:
        if not request.generate_premium_schedule:
            return {"status": "not_requested", "schedule": [], "summary": None}
        if not policy:
            return {"status": "not_available", "schedule": [], "summary": None}
        return ProductPolicyPremiumScheduleService(self.db).generate_schedule(
            company_id,
            policy,
            frequency=request.premium_frequency,
            total_premium=policy.premium_amount,
            duration_months=max(1, ((policy.end_date.year - policy.start_date.year) * 12) + (policy.end_date.month - policy.start_date.month)) if policy.start_date and policy.end_date else 12,
            start_date=policy.start_date,
            grace_period_days=request.premium_grace_period_days,
        )

    @staticmethod
    def _generate_quote_number(product_code: Optional[str]) -> str:
        prefix = (product_code or "CATALOG")[:8].upper().replace("-", "_")
        return f"{prefix}-{utcnow().strftime('%Y%m%d')}-{str(uuid4())[:8].upper()}"

    @staticmethod
    def _coverage_amount(quote_result: dict[str, Any]) -> Decimal:
        values = [item.get("limit_amount") for item in quote_result.get("coverage_breakdown", []) if item.get("limit_amount")]
        if values:
            return max(Decimal(str(value)) for value in values)
        return Decimal(str(quote_result.get("rating_base") or 0))

    @staticmethod
    def _risk_score(quote_result: dict[str, Any]) -> Decimal:
        base = Decimal("10")
        if quote_result.get("referral_required"):
            base += Decimal("40")
        if quote_result.get("decision") == "declined":
            base += Decimal("80")
        base += Decimal(str(len(quote_result.get("underwriting_decisions", [])) * 10))
        return min(base, Decimal("99.99"))

    @staticmethod
    def _mapped_decision(decision: Optional[str]) -> str:
        if decision in {"approved", "approve"}:
            return "approve"
        if decision in {"declined", "decline"}:
            return "decline"
        return "refer"

    @staticmethod
    def _required_documents(quote_result: dict[str, Any]) -> list[str]:
        documents = ["identity_verification", "proof_of_address"]
        if quote_result.get("product_line") == "car":
            documents.extend(["vehicle_registration", "driving_licence"])
        if quote_result.get("referral_required"):
            documents.append("underwriter_referral_review")
        return documents

    @classmethod
    def _build_response(
        cls,
        quote: Quote,
        quote_result: dict[str, Any],
        policy: Optional[Policy],
        idempotent: bool,
        document_packet: Optional[dict[str, Any]] = None,
        schedule_packet: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        document_packet = document_packet or {"status": "not_requested", "documents": []}
        schedule_packet = schedule_packet or {"status": "not_requested", "schedule": [], "summary": None}
        return {
            "status": "policy_issued" if policy else "quote_acquired",
            "quote_id": quote.id,
            "quote_number": quote.quote_number,
            "quote_status": quote.status,
            "policy_id": policy.id if policy else None,
            "policy_number": policy.policy_number if policy else None,
            "policy_status": policy.status if policy else None,
            "decision": cls._mapped_decision(quote_result.get("decision")),
            "product_quote": quote_result,
            "document_status": document_packet.get("status", "not_requested"),
            "documents": document_packet.get("documents", []),
            "premium_schedule_status": schedule_packet.get("status", "not_requested"),
            "premium_schedule": schedule_packet.get("schedule", []),
            "premium_schedule_summary": schedule_packet.get("summary"),
            "idempotent": idempotent,
        }

    @classmethod
    def _jsonable(cls, value: Any) -> Any:
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, (date,)):
            return value.isoformat()
        if isinstance(value, dict):
            return {str(key): cls._jsonable(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [cls._jsonable(item) for item in value]
        return value
