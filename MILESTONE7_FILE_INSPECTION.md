### product_policy_acquisition_service.py
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
            return self._build_response(existing_quote, quote_result, policy, idempotent=True)

        quote = self._create_quote(company_id, request, quote_result, created_by)
        decision = self._create_underwriting_decision(company_id, quote, request, quote_result)
        self._create_snapshot(company_id, quote, decision, request, quote_result)
        self.db.commit()
        self.db.refresh(quote)

        policy: Optional[Policy] = None
        if request.auto_issue_policy and self._is_approved(quote_result):
            policy = self._issue_policy(quote, request, created_by)

        return self._build_response(quote, quote_result, policy, idempotent=False)

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

    @staticmethod
    def _generate_quote_number(product_code: Optional[str]) -> str:
        prefix = (product_code or "CATALOG")[:8].upper().replace("-", "_")
        return f"{prefix}-{utcnow().strftime('%Y%m%d')}-{str(uuid4())[:8].upper()}"

    @staticmethod
    def _coverage_amount(quote_result: dict[str, Any]) -> Decimal:
        values = [item.get("limit_amount") for item in quote_result.get("coverage_breakdown", []) if item.get("limit_amount")]
### product_catalog schema tail
"""
Pydantic schemas for the Milestone 4 product and coverage engine.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


ProductLine = Literal["car", "travel", "home"]
ProductStatus = Literal["draft", "active", "retired", "archived"]
VersionStatus = Literal["draft", "active", "retired", "archived"]


class CoverageOptionBase(BaseModel):
    code: str
    label: str
    option_type: str = "limit"
    limit_amount: Optional[Decimal] = None
    deductible_amount: Optional[Decimal] = None
    premium_delta: Decimal = Decimal("0")
    rate_multiplier: Decimal = Decimal("1")
    configuration: dict[str, Any] = Field(default_factory=dict)
    is_default: bool = False
    is_active: bool = True
    display_order: int = 100


class CoverageOptionCreate(CoverageOptionBase):
    pass


class CoverageOptionUpdate(BaseModel):
    code: Optional[str] = None
    label: Optional[str] = None
    option_type: Optional[str] = None
    limit_amount: Optional[Decimal] = None
    deductible_amount: Optional[Decimal] = None
    premium_delta: Optional[Decimal] = None
    rate_multiplier: Optional[Decimal] = None
    configuration: Optional[dict[str, Any]] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class CoverageOptionResponse(CoverageOptionBase):
    id: UUID
    company_id: UUID
    coverage_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CoverageDefinitionBase(BaseModel):
    code: str
    name: str
    coverage_type: str
    description: Optional[str] = None
    is_required: bool = False
    default_limit: Optional[Decimal] = None
    minimum_limit: Optional[Decimal] = None
    maximum_limit: Optional[Decimal] = None
    default_deductible: Optional[Decimal] = None
    exclusions: list[dict[str, Any]] = Field(default_factory=list)
    conditions: list[dict[str, Any]] = Field(default_factory=list)
    display_order: int = 100
    is_active: bool = True


class CoverageDefinitionCreate(CoverageDefinitionBase):
    options: list[CoverageOptionCreate] = Field(default_factory=list)


class CoverageDefinitionUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    coverage_type: Optional[str] = None
    description: Optional[str] = None
    is_required: Optional[bool] = None
    default_limit: Optional[Decimal] = None
    minimum_limit: Optional[Decimal] = None
    maximum_limit: Optional[Decimal] = None
    default_deductible: Optional[Decimal] = None
    exclusions: Optional[list[dict[str, Any]]] = None
    conditions: Optional[list[dict[str, Any]]] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class CoverageDefinitionResponse(CoverageDefinitionBase):
    id: UUID
    company_id: UUID
    product_version_id: UUID
    options: list[CoverageOptionResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RatingFactorBase(BaseModel):
    code: str
    name: str
    factor_type: str
    applies_to: str
    input_path: str
    operator: str = "equals"
    value: Optional[str] = None
    factor: Decimal = Decimal("1")
    amount: Decimal = Decimal("0")
    priority: int = 100
    configuration: dict[str, Any] = Field(default_factory=dict)
    reason_code: Optional[str] = None
    is_active: bool = True


class RatingFactorCreate(RatingFactorBase):
    pass


class RatingFactorUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    factor_type: Optional[str] = None
    applies_to: Optional[str] = None
    input_path: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[str] = None
    factor: Optional[Decimal] = None
    amount: Optional[Decimal] = None
    priority: Optional[int] = None
    configuration: Optional[dict[str, Any]] = None
    reason_code: Optional[str] = None
    is_active: Optional[bool] = None


class RatingFactorResponse(RatingFactorBase):
    id: UUID
    company_id: UUID
    product_version_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProductUnderwritingRuleBase(BaseModel):
    code: str
    name: str
    rule_type: str = "eligibility"
    decision_effect: str = "refer"
    condition: dict[str, Any] = Field(default_factory=dict)
    message: Optional[str] = None
    authority_level: Optional[str] = None
    priority: int = 100
    is_active: bool = True


class ProductUnderwritingRuleCreate(ProductUnderwritingRuleBase):
    pass


class ProductUnderwritingRuleUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    rule_type: Optional[str] = None
    decision_effect: Optional[str] = None
    condition: Optional[dict[str, Any]] = None
    message: Optional[str] = None
    authority_level: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class ProductUnderwritingRuleResponse(ProductUnderwritingRuleBase):
    id: UUID
    company_id: UUID
    product_version_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class QuoteWizardSchemaBase(BaseModel):
    channel: str = "portal"
    schema_version: str = "1.0"
    title: str
    steps: list[dict[str, Any]] = Field(default_factory=list)
    validation_schema: dict[str, Any] = Field(default_factory=dict)
    ui_schema: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True

    @field_validator("steps")
    @classmethod
    def require_wizard_steps(cls, value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not value:
            raise ValueError("Quote wizard schema must include at least one step")
        return value


class QuoteWizardSchemaCreate(QuoteWizardSchemaBase):
    pass


class QuoteWizardSchemaUpdate(BaseModel):
    channel: Optional[str] = None
    schema_version: Optional[str] = None
    title: Optional[str] = None
    steps: Optional[list[dict[str, Any]]] = None
    validation_schema: Optional[dict[str, Any]] = None
    ui_schema: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class QuoteWizardSchemaResponse(QuoteWizardSchemaBase):
    id: UUID
    company_id: UUID
    product_version_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProductVersionBase(BaseModel):
    version: str
    status: VersionStatus = "draft"
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    base_currency: str = "USD"
    rating_strategy: str = "factor_table"
    base_rate: Decimal = Decimal("0")
    minimum_premium: Decimal = Decimal("0")
    taxes_and_fees: list[dict[str, Any]] = Field(default_factory=list)
    configuration: dict[str, Any] = Field(default_factory=dict)


class ProductVersionCreate(ProductVersionBase):
    coverages: list[CoverageDefinitionCreate] = Field(default_factory=list)
    rating_factors: list[RatingFactorCreate] = Field(default_factory=list)
    underwriting_rules: list[ProductUnderwritingRuleCreate] = Field(default_factory=list)
    wizard_schemas: list[QuoteWizardSchemaCreate] = Field(default_factory=list)


class ProductVersionUpdate(BaseModel):
    version: Optional[str] = None
    status: Optional[VersionStatus] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    base_currency: Optional[str] = None
    rating_strategy: Optional[str] = None
    base_rate: Optional[Decimal] = None
    minimum_premium: Optional[Decimal] = None
    taxes_and_fees: Optional[list[dict[str, Any]]] = None
    configuration: Optional[dict[str, Any]] = None


class ProductVersionResponse(ProductVersionBase):
    id: UUID
    company_id: UUID
    product_id: UUID
    coverages: list[CoverageDefinitionResponse] = Field(default_factory=list)
    rating_factors: list[RatingFactorResponse] = Field(default_factory=list)
    underwriting_rules: list[ProductUnderwritingRuleResponse] = Field(default_factory=list)
    wizard_schemas: list[QuoteWizardSchemaResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class InsuranceProductBase(BaseModel):
    code: str
    name: str
    product_line: ProductLine
    description: Optional[str] = None
    status: ProductStatus = "active"
    is_active: bool = True
    display_order: int = 100
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class InsuranceProductCreate(InsuranceProductBase):
    versions: list[ProductVersionCreate] = Field(default_factory=list)


class InsuranceProductUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    product_line: Optional[ProductLine] = None
    description: Optional[str] = None
    status: Optional[ProductStatus] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None
    metadata_json: Optional[dict[str, Any]] = None


class InsuranceProductResponse(InsuranceProductBase):
    id: UUID
    company_id: UUID
    versions: list[ProductVersionResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProductCatalogListResponse(BaseModel):
    products: list[InsuranceProductResponse]
    total: int
    page: int = 1
    page_size: int = 50


class ProductCatalogSeedResponse(BaseModel):
    status: str
    created_products: int
    updated_products: int
    products: list[InsuranceProductResponse]
### product_catalog endpoint relevant
"""
Product catalog API endpoints for Milestone 4.

These endpoints expose tenant-scoped configuration for car, travel, and home
insurance products, including active product versions, coverage definitions,
rating factors, underwriting rules, and quote wizard schemas.
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.product_catalog import (
    CoverageDefinition,
    CoverageOption,
    InsuranceProduct,
    ProductUnderwritingRule,
    ProductVersion,
    QuoteWizardSchema,
    RatingFactor,
)
from app.models.user import User
from app.schemas.product_catalog import (
    CoverageDefinitionCreate,
    CoverageDefinitionResponse,
    CoverageDefinitionUpdate,
    CoverageOptionCreate,
    CoverageOptionResponse,
    CoverageOptionUpdate,
    InsuranceProductCreate,
    InsuranceProductResponse,
    InsuranceProductUpdate,
    ProductCatalogListResponse,
    ProductCatalogSeedResponse,
    ProductCatalogSummaryItem,
    ProductCatalogSummaryResponse,
    ProductPolicyAcquisitionRequest,
    ProductPolicyAcquisitionResponse,
    ProductQuoteRecommendationRequest,
    ProductQuoteRecommendationResponse,
    ProductQuoteRequest,
    ProductQuoteResponse,
    ProductUnderwritingRuleCreate,
    ProductUnderwritingRuleResponse,
    ProductUnderwritingRuleUpdate,
    ProductVersionCreate,
    ProductVersionResponse,
    ProductVersionUpdate,
    QuoteWizardSchemaCreate,
    QuoteWizardSchemaResponse,
    QuoteWizardSchemaUpdate,
    RatingFactorCreate,
    RatingFactorResponse,
    RatingFactorUpdate,
)
from app.services.product_catalog_service import ProductCatalogService
from app.services.product_policy_acquisition_service import ProductPolicyAcquisitionService
from app.services.product_quote_engine_service import ProductQuoteEngineService

router = APIRouter()


def _get_product_or_404(db: Session, company_id: UUID, product_id: UUID) -> InsuranceProduct:
    product = ProductCatalogService(db).get_product(company_id, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def _get_version_or_404(db: Session, company_id: UUID, version_id: UUID) -> ProductVersion:
    version = db.query(ProductVersion).filter(ProductVersion.company_id == company_id, ProductVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Product version not found")
    return version


def _get_coverage_or_404(db: Session, company_id: UUID, coverage_id: UUID) -> CoverageDefinition:
    coverage = db.query(CoverageDefinition).filter(CoverageDefinition.company_id == company_id, CoverageDefinition.id == coverage_id).first()
    if not coverage:
        raise HTTPException(status_code=404, detail="Coverage not found")
    return coverage


@router.post("/seed-defaults", response_model=ProductCatalogSeedResponse)
def seed_default_product_catalog(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Seed or refresh default car, travel, and home product catalog definitions for the current tenant."""
    service = ProductCatalogService(db)
    products, created, updated = service.seed_defaults(current_user.company_id, current_user.id)
    return {"status": "success", "created_products": created, "updated_products": updated, "products": products}


@router.get("/summary", response_model=ProductCatalogSummaryResponse)
def get_product_catalog_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return compact active product catalog metadata suitable for AI and quote wizard selection."""
    summary = ProductCatalogService(db).get_active_catalog_summary(current_user.company_id)
    return {"products": [ProductCatalogSummaryItem(**item) for item in summary], "total": len(summary)}


@router.post("/quote/calculate", response_model=ProductQuoteResponse)
def calculate_product_quote(
    quote_request: ProductQuoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calculate a deterministic product-catalog quote for car, travel, or home insurance."""
    try:
        return ProductQuoteEngineService(db).calculate_quote(current_user.company_id, quote_request)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/quote/recommendations", response_model=ProductQuoteRecommendationResponse)
def recommend_product_quotes(
    recommendation_request: ProductQuoteRecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return ranked product-catalog quote recommendations for the current tenant."""
    recommendations = ProductQuoteEngineService(db).recommend_quotes(current_user.company_id, recommendation_request)
    recommended = next((item for item in recommendations if item.get("is_eligible")), None)
    return {
        "recommendations": recommendations,
        "total": len(recommendations),
        "recommended_product_id": recommended.get("product_id") if recommended else None,
    }


@router.post("/quote/acquire", response_model=ProductPolicyAcquisitionResponse, status_code=status.HTTP_201_CREATED)
def acquire_product_policy(
    acquisition_request: ProductPolicyAcquisitionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Persist an approved catalog quote as a policy-ready quote and optionally issue a policy."""
    try:
        return ProductPolicyAcquisitionService(db).acquire_policy(
            current_user.company_id,
            acquisition_request,
            current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/products", response_model=InsuranceProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: InsuranceProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a tenant-scoped product with optional nested version, coverage, factor, rule, and wizard definitions."""
    existing = db.query(InsuranceProduct).filter(
        InsuranceProduct.company_id == current_user.company_id,
        InsuranceProduct.code == product_data.code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Product code already exists for this company")
    return ProductCatalogService(db).create_product(current_user.company_id, product_data, current_user.id)


@router.get("/products", response_model=ProductCatalogListResponse)
def list_products(
    product_line: Optional[str] = Query(None, description="Filter by product line: car, travel, or home"),
    active_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List tenant-scoped insurance products and nested version definitions."""
    products, total = ProductCatalogService(db).list_products(current_user.company_id, product_line, active_only, page, page_size)
    return {"products": products, "total": total, "page": page, "page_size": page_size}


@router.get("/products/{product_id}", response_model=InsuranceProductResponse)
def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get one product catalog entry with versions, coverages, rating factors, rules, and wizard schemas."""
    return _get_product_or_404(db, current_user.company_id, product_id)


@router.put("/products/{product_id}", response_model=InsuranceProductResponse)
def update_product(
    product_id: UUID,
    product_data: InsuranceProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update product-level metadata without mutating versioned coverage definitions."""
    product = _get_product_or_404(db, current_user.company_id, product_id)
    for field, value in product_data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete a product catalog entry and its nested versions for the tenant."""
    product = _get_product_or_404(db, current_user.company_id, product_id)
    db.delete(product)
    db.commit()
    return None


@router.post("/products/{product_id}/versions", response_model=ProductVersionResponse, status_code=status.HTTP_201_CREATED)
def create_product_version(
    product_id: UUID,
    version_data: ProductVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new product version with optional nested coverage and wizard configuration."""
    product = _get_product_or_404(db, current_user.company_id, product_id)
    existing = db.query(ProductVersion).filter(
        ProductVersion.company_id == current_user.company_id,
        ProductVersion.product_id == product_id,
        ProductVersion.version == version_data.version,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Product version already exists")
    return ProductCatalogService(db).add_version(current_user.company_id, product, version_data, current_user.id)


@router.put("/versions/{version_id}", response_model=ProductVersionResponse)
def update_product_version(
    version_id: UUID,
    version_data: ProductVersionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update product version metadata such as status, dates, base rate, and minimum premium."""
    version = _get_version_or_404(db, current_user.company_id, version_id)
    for field, value in version_data.model_dump(exclude_unset=True).items():
        setattr(version, field, value)
    db.commit()
    db.refresh(version)
    return version


@router.post("/versions/{version_id}/coverages", response_model=CoverageDefinitionResponse, status_code=status.HTTP_201_CREATED)
### document_service.py
import os
import re
import json
import html
import qrcode
import base64
import secrets
from pathlib import Path
from io import BytesIO
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from app.core.config import settings
from app.core.time import utcnow
from app.models.policy import Policy
from app.models.company import Company
from app.models.client import Client
from app.models.document import Document, DocumentLabel
from app.models.document_template import DocumentTemplate


class DocumentService:
    def __init__(self):
        project_root = Path(settings.PROJECT_ROOT).resolve().parent
        self.template_source_dir = project_root / "ai_docs" / "references" / "examples" / "insurance_docs" / "docs"
        self.output_dir = project_root / "static" / "documents"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._html_tags = {
            "html", "head", "body", "title", "style", "script", "div", "span", "p", "h1", "h2", "h3", "h4",
            "ul", "ol", "li", "table", "thead", "tbody", "tr", "th", "td", "strong", "em", "small", "br"
        }

    def _generate_qr_code(self, data: str) -> str:
        """Generates a QR code and returns it as a base64 encoded string."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    def _generate_qr_png_bytes(self, data: str) -> bytes:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return buffered.getvalue()

    def _generate_verification_code(self) -> str:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return "".join(secrets.choice(alphabet) for _ in range(16))

    def _format_currency(self, amount: float, currency: str = "GBP") -> str:
        symbol = "Â£" if currency == "GBP" else "$" if currency == "USD" else "â‚¬"
        return f"{symbol}{amount:,.2f}"

    def _extract_placeholders(self, html_content: str) -> List[str]:
        raw = set(re.findall(r"<([a-zA-Z0-9_]+)>", html_content))
        return sorted(tag for tag in raw if tag not in self._html_tags)

    def _build_data_mapping(
        self,
        policy: Policy,
        client: Client,
        company: Company,
        vehicle: Optional[dict],
    ) -> Dict[str, Any]:
        vehicle_data = vehicle or {}
        return {
            "nom_client": client.display_name,
            "adresse_client": getattr(client, "address", "Address Not Provided"),
            "email_client": getattr(client, "email", ""),
            "telephone_client": getattr(client, "phone", ""),
            "compagnie_dassurance": company.name,
            "compagnie_logo": getattr(company, "logo_url", ""),
            "compagnie_couleur_primaire": getattr(company, "primary_color", "#00539F"),
            "compagnie_couleur_secondaire": getattr(company, "secondary_color", "#333333"),
            "compagnie_adresse": getattr(company, "address", "Company Address"),
            "compagnie_website": getattr(company, "website", "www.tinsur.ai"),
            "compagnie_telephone": getattr(company, "phone", "Contact Support"),
            "numero_police": policy.policy_number,
            "date_debut": policy.start_date.strftime("%d/%m/%Y") if policy.start_date else "",
            "date_fin": policy.end_date.strftime("%d/%m/%Y") if policy.end_date else "",
            "prime_totale": self._format_currency(float(policy.premium_amount or 0)),
            "montant_couverture": self._format_currency(float(policy.coverage_amount or 0)),
            "type_assurance": policy.policy_type.name if policy.policy_type else "General",
            "marque": vehicle_data.get("make", "N/A"),
            "modele": vehicle_data.get("model", "N/A"),
            "immatriculation": vehicle_data.get("registration", vehicle_data.get("registrationNumber", "N/A")),
            "numero_vehicule": vehicle_data.get("vin", ""),
        }

    def _html_to_text(self, html_content: str) -> str:
        cleaned = re.sub(r"<(script|style)[^>]*>.*?</\\1>", "", html_content, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<br\\s*/?>", "\n", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"</p>", "\n\n", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"</li>", "\n", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"<[^>]+>", "", cleaned)
        cleaned = html.unescape(cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    def _render_pdf(
        self,
        html_content: str,
        output_path: Path,
        company: Company,
        client: Client,
        verification_code: str,
        qr_payload: str,
    ) -> None:
        doc = SimpleDocTemplate(str(output_path), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(company.name, styles["Title"]))
        story.append(Paragraph(f"Client: {client.display_name}", styles["Normal"]))
        story.append(Paragraph(f"Verification Code: {verification_code}", styles["Normal"]))
        story.append(Spacer(1, 12))

        qr_bytes = self._generate_qr_png_bytes(qr_payload)
        qr_img = Image(BytesIO(qr_bytes), width=120, height=120)
        story.append(qr_img)
        story.append(Spacer(1, 16))

        text = self._html_to_text(html_content)
        for paragraph in text.split("\n\n"):
            story.append(Paragraph(paragraph.replace("\n", "<br/>"), styles["BodyText"]))
            story.append(Spacer(1, 8))

        doc.build(story)

    def _load_templates_from_files(self) -> List[Dict[str, Any]]:
        if not self.template_source_dir.exists():
            return []

        templates = []
        for file_path in sorted(self.template_source_dir.glob("*.html")):
            content = file_path.read_text(encoding="utf-8")
            placeholders = self._extract_placeholders(content)
            templates.append({
                "code": file_path.stem.lower(),
                "name": file_path.stem.replace("_", " "),
                "description": None,
                "language": "fr",
                "template_html": content,
                "placeholders": placeholders,
                "source_path": str(file_path),
            })
        return templates

    def _ensure_templates_loaded(self, db) -> None:
        templates = self._load_templates_from_files()
        if not templates:
            return

        for tmpl in templates:
            existing = db.query(DocumentTemplate).filter(DocumentTemplate.code == tmpl["code"]).first()
            if existing:
                existing.name = tmpl["name"]
                existing.description = tmpl["description"]
                existing.language = tmpl["language"]
                existing.template_html = tmpl["template_html"]
                existing.placeholders = tmpl["placeholders"]
                existing.source_path = tmpl["source_path"]
            else:
                db.add(DocumentTemplate(**tmpl))
        db.commit()

    def _get_policy_vehicle(self, policy: Policy, client: Client) -> dict:
        if policy.details and isinstance(policy.details, dict):
            vehicle = policy.details.get("vehicle") or {}
            if vehicle:
                return {
                    "make": vehicle.get("make"),
                    "model": vehicle.get("model"),
                    "registrationNumber": vehicle.get("registrationNumber"),
                    "vin": vehicle.get("vin"),
                }
        if client.automobile_details:
            auto = client.automobile_details[0]
            return {
                "make": getattr(auto, "vehicle_make", None),
                "model": getattr(auto, "vehicle_model", None),
                "registration": getattr(auto, "vehicle_registration", None),
                "vin": getattr(auto, "vehicle_vin", None),
            }
        return {}

    def _generate_unique_code(self, db) -> str:
        code = self._generate_verification_code()
        while db.query(Document).filter(Document.verification_code == code).first():
            code = self._generate_verification_code()
        return code

    def generate_documents(self, db, policy: Policy, client: Client, company: Company) -> List[str]:
        """
        Generates all insurance documents for a given policy.
        Returns a list of generated file paths (relative to static/documents).
        """
        self._ensure_templates_loaded(db)

        policy_dir = self.output_dir / str(policy.id)
        policy_dir.mkdir(parents=True, exist_ok=True)

        generated_files = []
        vehicle = self._get_policy_vehicle(policy, client)
        data_mapping = self._build_data_mapping(policy, client, company, vehicle)

        templates = db.query(DocumentTemplate).order_by(DocumentTemplate.created_at.asc()).all()
        for template in templates:
            content = template.template_html
            placeholders = template.placeholders or self._extract_placeholders(content)
            for key, value in data_mapping.items():
                content = content.replace(f"<{key}>", str(value))

            verification_code = self._generate_unique_code(db)
            now = utcnow()
            doc_specific_mapping = {
                "reference_document_interne": verification_code,
                "reference_document_produit": verification_code,
                "reference_template_document": template.code,
                "reference_document_version": "v1",
                "date_emission_document": now.strftime("%d/%m/%Y"),
                "horodatage_emission_document": now.strftime("%Y-%m-%d %H:%M:%S"),
                "date_impression": now.strftime("%d/%m/%Y"),
                "heure_impression": now.strftime("%H:%M"),
                "numero_enregistrement_compagnie": getattr(company, "system_registration_number", "") or "",
                "numero_enregistrement_siege_social": getattr(company, "system_registration_number", "") or "",
                "numero_enregistrement_siege": getattr(company, "system_registration_number", "") or "",
                "reference_client": str(client.id),
                "reference_client_complete": str(client.id),
                "type_police": data_mapping.get("type_assurance", ""),
                "type_police_description": data_mapping.get("type_assurance", ""),
            }
            for key, value in doc_specific_mapping.items():
                content = content.replace(f"<{key}>", str(value))

            for placeholder in placeholders:
                if placeholder not in data_mapping and placeholder not in doc_specific_mapping:
                    content = content.replace(f"<{placeholder}>", "")

            qr_payload = json.dumps({
                "company_id": str(company.id),
                "company_name": company.name,
                "client_id": str(client.id),
### documents endpoint policy sections
    settings: ShareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    if doc.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    doc.visibility = settings.visibility
    doc.scope = settings.scope
    doc.is_shareable = settings.is_shareable
    doc.reshare_rule = settings.reshare_rule
    
    db.commit()
    return {"status": "success", "message": "Settings updated"}


@router.get("/policy/{policy_id}", response_model=List[str])
def list_policy_documents(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List auto-generated insurance documents for a specific policy."""
    repo = PolicyRepository(db)
    policy = repo.get_by_id(policy_id)
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
        
    # Access Control: Company or Client
    if policy.company_id != current_user.company_id:
         # Check if client user owns the policy
         if current_user.role == "client":
             from app.models.client import Client
             client = db.query(Client).filter(Client.user_id == current_user.id).first()
             if not client or str(client.id) != str(policy.client_id):
                 raise HTTPException(status_code=403, detail="Not authorized")
         else:
             raise HTTPException(status_code=403, detail="Not authorized")

    docs = db.query(Document).filter(
        Document.policy_id == policy_id,
        Document.company_id == policy.company_id
    ).order_by(Document.created_at.asc()).all()

    return [doc.file_url for doc in docs if doc.file_url]

@router.get("/policy/{policy_id}/{filename}")
def get_policy_document(
    policy_id: UUID,
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Serve a specific auto-generated document."""
    # Access Control
    repo = PolicyRepository(db)
    policy = repo.get_by_id(policy_id)
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if policy.company_id != current_user.company_id:
         if current_user.role == "client":
             from app.models.client import Client
             client = db.query(Client).filter(Client.user_id == current_user.id).first()
             if not client or str(client.id) != str(policy.client_id):
                 raise HTTPException(status_code=403, detail="Not authorized")
         else:
             raise HTTPException(status_code=403, detail="Not authorized")

    safe_filename = os.path.basename(filename)
    file_path = os.path.join(str(document_service.output_dir), str(policy_id), safe_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document not found")

    return FileResponse(file_path)


@router.post("/policy/{policy_id}/generate")
def generate_policy_documents(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger document generation for a policy (insurance certificate, insurance card, etc.).
    Uses the DocumentService template engine. Returns a list of generated file URLs.
    Requires company_admin or higher role.
    """
    if current_user.role not in ("company_admin", "super_admin", "manager"):
        raise HTTPException(status_code=403, detail="Not authorized to generate documents")

    repo = PolicyRepository(db)
    policy = repo.get_by_id(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    if policy.company_id != current_user.company_id and current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Not authorized for this policy")

    # Fetch required related objects
    from app.models.client import Client
    from app.models.company import Company as CompanyModel

    client = db.query(Client).filter(Client.id == policy.client_id).first()
    company = db.query(CompanyModel).filter(CompanyModel.id == policy.company_id).first()

    if not client or not company:
        raise HTTPException(status_code=422, detail="Policy is missing client or company data")

    try:
        generated_paths = document_service.generate_documents(db, policy, client, company)
    except Exception as exc:
        logger.error("Document generation failed for policy %s: %s", policy_id, exc)
        raise HTTPException(status_code=500, detail=f"Document generation failed: {exc}")

    return {
        "policy_id": str(policy_id),
        "generated": len(generated_paths),
        "files": generated_paths,
        "message": f"{len(generated_paths)} document(s) generated successfully.",
    }
### policy_service.py relevant
48:    def generate_policy_number(self, company_id: UUID, policy_type_code: str) -> str:
65:        if not quote or quote.status not in ['accepted', 'policy_created']:
123:            status='active',
151:        quote.status = 'policy_created'
177:    def create_policy(
208:            status='active',
276:    def renew_policy(
295:        policy.status = 'active'
299:    def cancel_policy(
313:            policy.status = 'expired'
339:            Endorsement.status.in_(['draft', 'pending_approval'])
363:            status='draft',
382:            created_endorsement.status = 'pending_approval'
390:        if not endorsement or endorsement.status not in ['draft', 'approved']:
404:        # 2. Update status and timestamp
405:        endorsement.status = 'active'
430:    def reinstate_policy(self, policy_id: UUID) -> Optional[Policy]:
436:        if policy.status not in ['canceled', 'lapsed', 'expired']:
439:        policy.status = 'active'
"""
Policy service for business logic operations.
"""
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date, timedelta
import random
from app.core.time import utcnow

from app.models.policy import Policy
from app.models.quote import Quote
from app.models.endorsement import Endorsement
from app.models.policy_type import PolicyType
from app.repositories.policy_repository import PolicyRepository
from app.repositories.quote_repository import QuoteRepository
from app.repositories.endorsement_repository import EndorsementRepository
from app.repositories.endorsement_repository import EndorsementRepository
from app.repositories.pos_inventory_repository import POSInventoryRepository
from app.services.reinsurance_service import ReinsuranceService
from app.services.archive_service import ArchiveService
from app.services.underwriting_service import UnderwritingService
from app.services.regulatory_service import RegulatoryService
from app.services.document_service import document_service
from app.models.underwriting import QuoteUnderwritingSnapshot
from app.repositories.client_repository import ClientRepository
from app.repositories.company_repository import CompanyRepository

class PolicyService:
    """Service for policy-related business logic."""
    
    def __init__(
        self, 
        policy_repo: PolicyRepository, 
        quote_repo: QuoteRepository,
        endorsement_repo: EndorsementRepository,
        pos_inventory_repo: Optional[POSInventoryRepository] = None
    ):
        self.policy_repo = policy_repo
        self.quote_repo = quote_repo
        self.endorsement_repo = endorsement_repo
        self.pos_inventory_repo = pos_inventory_repo
        self.reinsurance_service = ReinsuranceService(policy_repo.db)
        self.archive_service = ArchiveService(policy_repo.db)
        self.underwriting_service = UnderwritingService(policy_repo.db)
        self.regulatory_service = RegulatoryService(policy_repo.db)
    
    def generate_policy_number(self, company_id: UUID, policy_type_code: str) -> str:
        """Generate unique policy number."""
        timestamp = datetime.now().strftime('%Y%m%d')
        random_suffix = random.randint(10000, 99999)
        # Simplify code to first 3 chars if too long
        code_prefix = policy_type_code[:3].upper() if policy_type_code else "POL"
        return f"{code_prefix}-{timestamp}-{random_suffix}"
    
    def create_from_quote(
        self,
        quote_id: UUID,
        start_date: date,
        created_by: UUID
    ) -> Optional[Policy]:
        """Create a policy from an accepted quote with underwriting snapshot validation."""
        quote = self.quote_repo.get_by_id(quote_id)
        
        if not quote or quote.status not in ['accepted', 'policy_created']:
            return None
        
        if quote.is_expired:
            return None

        existing_policy = self.policy_repo.get_by_quote_id(quote_id)
        if existing_policy:
            return existing_policy

        snapshot = (
            self.policy_repo.db.query(QuoteUnderwritingSnapshot)
            .filter(QuoteUnderwritingSnapshot.quote_id == quote_id)
            .first()
        )
        if not snapshot:
            return None

        decision = None
        if snapshot.decision_snapshot:
            decision = snapshot.decision_snapshot.get("decision")
        if not decision and snapshot.decision:
            decision = snapshot.decision.decision
        if decision not in {"approve", "approved"}:
            return None

        if snapshot.valid_until and snapshot.valid_until < utcnow():
            return None
        
        # Calculate end_date based on duration
        end_date = start_date + timedelta(days=quote.duration_months * 30)
        
        # Get policy type code
        policy_type_code = "GEN"
        if quote.policy_type:
            policy_type_code = quote.policy_type.code
        else:
            # Try to fetch if not loaded
            policy_type = self.policy_repo.db.query(PolicyType).filter(PolicyType.id == quote.policy_type_id).first()
            if policy_type:
                policy_type_code = policy_type.code
        
        # Generate policy number
        policy_number = self.generate_policy_number(quote.company_id, policy_type_code)
        
        # Create policy
        policy = Policy(
            company_id=quote.company_id,
            client_id=quote.client_id,
            policy_type_id=quote.policy_type_id,
            quote_id=quote_id,
            policy_number=policy_number,
            coverage_amount=quote.coverage_amount,
            premium_amount=quote.final_premium,
            premium_frequency=quote.premium_frequency,
            start_date=start_date,
            end_date=end_date,

            status='active',
            details={
                **(quote.details or {}),
                "financial_snapshot": {
                    "apr_percent": float(quote.apr_percent or 0),
                    "arrangement_fee": float(quote.arrangement_fee or 0),
                    "extra_fee": float(quote.extra_fee or 0),
                    "total_financed_amount": float(quote.total_financed_amount or 0),
                    "monthly_installment": float(quote.monthly_installment or 0),
                    "total_installment_price": float(quote.total_installment_price or 0)
                },
                "underwriting_snapshot": {
                    "snapshot_id": str(snapshot.id),
                    "underwriting_decision_id": str(snapshot.underwriting_decision_id) if snapshot.underwriting_decision_id else None,
                    "rule_set_id": str(snapshot.rule_set_id) if snapshot.rule_set_id else None,
                    "decision": decision,
                    "valid_until": snapshot.valid_until.isoformat() if snapshot.valid_until else None,
                    "premium_breakdown": snapshot.premium_breakdown or {},
                    "policy_ready_payload": snapshot.policy_ready_payload or {},
                    "decision_snapshot": snapshot.decision_snapshot or {},
                    "normalized_payload": snapshot.normalized_payload or {},
                    "required_documents": (snapshot.policy_ready_payload or {}).get("required_documents", [])
                }
            },
            created_by=created_by
        )
        
        policy = self.policy_repo.create(policy)
        quote.status = 'policy_created'
        self.quote_repo.update(quote)
        
        # Trigger Reinsurance Cession
        self.reinsurance_service.process_policy_cessions(policy)
        
        # Archive Policy Document (Immutable Legal Proof)
        dummy_content = f"Policy Contract: {policy.policy_number}".encode()
        self.archive_service.archive_policy_document(policy.id, policy.policy_document_url, dummy_content)
        
        # Generate Policy Documents
        try:
            client_repo = ClientRepository(self.policy_repo.db)
            company_repo = CompanyRepository(self.policy_repo.db)
            
            client = client_repo.get_by_id(policy.client_id)
            company = company_repo.get_by_id(policy.company_id)
            
            if client and company:
                document_service.generate_documents(self.policy_repo.db, policy, client, company)
        except Exception as e:
            print(f"Error generating documents for policy {policy.id}: {e}")
            # Non-blocking error, log and continue
        
        return policy
    
    def create_policy(
        self,
        company_id: UUID,
        client_id: UUID,
        policy_type_id: UUID,
        coverage_amount: Decimal,
        premium_amount: Decimal,
        premium_frequency: str,
        start_date: date,
        end_date: date,
        created_by: UUID,
        sales_agent_id: Optional[UUID] = None,
        pos_location_id: Optional[UUID] = None,

        details: Optional[dict] = None,
        inventory_deductions: Optional[List[dict]] = None,
        services: Optional[List[dict]] = None
    ) -> Policy:
        """Create a policy directly (not from quote)."""
        policy_number = self.generate_policy_number(company_id, "GEN")
        
        policy = Policy(
            company_id=company_id,
            client_id=client_id,
            policy_type_id=policy_type_id,
            policy_number=policy_number,
            coverage_amount=coverage_amount,
            premium_amount=premium_amount,
            premium_frequency=premium_frequency,
            start_date=start_date,
            end_date=end_date,
            status='active',
            details=details or {},
            created_by=created_by,
            sales_agent_id=sales_agent_id,

            pos_location_id=pos_location_id
        )
        
        created_policy = self.policy_repo.create(policy)
        
        # Handle Policy Services
        if services:
            from app.models.policy_service import policy_service_association
            for svc in services:
                if 'service_id' in svc and 'price' in svc:
                    self.policy_repo.db.execute(
                        policy_service_association.insert().values(
                            policy_id=created_policy.id,
                            service_id=svc['service_id'],
                            price=svc['price']
                        )
                    )

        
        # Trigger Reinsurance Cession
        self.reinsurance_service.process_policy_cessions(created_policy)
        
        # Handle Inventory Deduction
        if self.pos_inventory_repo and pos_location_id and inventory_deductions:
            for item in inventory_deductions:
                item_id = item.get('item_id')
                quantity = item.get('quantity', 1)
                if item_id:
                    try:
                        self.pos_inventory_repo.deduct_inventory(
                            item_id=item_id,
                            quantity=quantity,
                            transaction_type='sale',
                            reference_id=created_policy.id,
                            created_by=created_by,
                            notes=f"Policy Sale: {created_policy.policy_number}"
                        )
                    except ValueError as e:
                        print(f"Inventory Error: {e}")
                        # Optionally rollback or just log? 
                        # Ideally should stop policy creation if strict, 
                        # but for now let's just log and continue or add warning to notes.
                        
                        print(f"Inventory Error: {e}")
                        # Optionally rollback or just log? 
                        # Ideally should stop policy creation if strict, 
                        # but for now let's just log and continue or add warning to notes.
                        
