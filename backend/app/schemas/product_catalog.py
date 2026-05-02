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


class ProductCatalogSummaryItem(BaseModel):
    product_id: UUID
    code: str
    name: str
    product_line: ProductLine
    active_version_id: Optional[UUID] = None
    active_version: Optional[str] = None
    coverage_count: int = 0
    rating_factor_count: int = 0
    underwriting_rule_count: int = 0
    wizard_channels: list[str] = Field(default_factory=list)


class ProductCatalogSummaryResponse(BaseModel):
    products: list[ProductCatalogSummaryItem]
    total: int


class ProductQuoteCoverageSelection(BaseModel):
    coverage_code: str
    option_code: Optional[str] = None
    limit_amount: Optional[Decimal] = None
    deductible_amount: Optional[Decimal] = None
    is_selected: bool = True


class ProductQuoteRequest(BaseModel):
    product_id: Optional[UUID] = None
    product_code: Optional[str] = None
    product_line: Optional[ProductLine] = None
    applicant_data: dict[str, Any] = Field(default_factory=dict)
    risk_data: dict[str, Any] = Field(default_factory=dict)
    coverage_selections: list[ProductQuoteCoverageSelection] = Field(default_factory=list)
    channel: str = "portal"
    term_months: int = Field(default=12, ge=1, le=36)

    @field_validator("product_code")
    @classmethod
    def normalize_product_code(cls, value: Optional[str]) -> Optional[str]:
        return value.upper() if value else value


class ProductQuoteCoverageBreakdown(BaseModel):
    coverage_code: str
    coverage_name: str
    option_code: Optional[str] = None
    option_label: Optional[str] = None
    limit_amount: Optional[Decimal] = None
    deductible_amount: Optional[Decimal] = None
    premium_delta: Decimal = Decimal("0")
    rate_multiplier: Decimal = Decimal("1")


class ProductQuoteFactorBreakdown(BaseModel):
    code: str
    name: str
    factor_type: str
    applies_to: str
    input_path: str
    matched_value: Optional[Any] = None
    factor: Decimal = Decimal("1")
    amount: Decimal = Decimal("0")
    reason_code: Optional[str] = None


class ProductQuoteUnderwritingDecision(BaseModel):
    code: str
    name: str
    decision_effect: str
    message: Optional[str] = None
    authority_level: Optional[str] = None


class ProductQuoteTaxFeeBreakdown(BaseModel):
    code: str
    name: Optional[str] = None
    fee_type: str
    amount: Decimal


class ProductQuoteResponse(BaseModel):
    product_id: UUID
    product_code: str
    product_name: str
    product_line: ProductLine
    product_version_id: UUID
    product_version: str
    currency: str
    term_months: int
    rating_base: Decimal
    base_premium: Decimal
    subtotal_premium: Decimal
    taxes_and_fees_total: Decimal
    estimated_premium: Decimal
    is_eligible: bool
    referral_required: bool = False
    decision: str
    decision_reasons: list[str] = Field(default_factory=list)
    coverage_breakdown: list[ProductQuoteCoverageBreakdown] = Field(default_factory=list)
    factor_breakdown: list[ProductQuoteFactorBreakdown] = Field(default_factory=list)
    underwriting_decisions: list[ProductQuoteUnderwritingDecision] = Field(default_factory=list)
    taxes_and_fees: list[ProductQuoteTaxFeeBreakdown] = Field(default_factory=list)
    wizard_schema: Optional[QuoteWizardSchemaResponse] = None


class ProductQuoteRecommendationRequest(BaseModel):
    product_line: Optional[ProductLine] = None
    applicant_data: dict[str, Any] = Field(default_factory=dict)
    risk_data: dict[str, Any] = Field(default_factory=dict)
    coverage_selections: list[ProductQuoteCoverageSelection] = Field(default_factory=list)
    channel: str = "portal"
    term_months: int = Field(default=12, ge=1, le=36)
    include_referred: bool = True


class ProductQuoteRecommendationResponse(BaseModel):
    recommendations: list[ProductQuoteResponse]
    total: int
    recommended_product_id: Optional[UUID] = None


class ProductPolicyAcquisitionRequest(BaseModel):
    client_id: UUID
    quote_request: ProductQuoteRequest
    policy_type_id: Optional[UUID] = None
    requested_start_date: Optional[date] = None
    premium_frequency: str = "annual"
    sale_channel: str = "online"
    valid_for_days: int = Field(default=30, ge=1, le=90)
    auto_issue_policy: bool = True
    allow_referred_quote: bool = False
    generate_policy_documents: bool = True
    regenerate_policy_documents: bool = False
    idempotency_key: Optional[str] = Field(default=None, max_length=120)
    notes: Optional[str] = None


class ProductPolicyDocumentItem(BaseModel):
    document_id: Optional[UUID] = None
    name: str
    file_url: str
    file_type: Optional[str] = None
    verification_code: Optional[str] = None


class ProductPolicyAcquisitionResponse(BaseModel):
    status: str
    quote_id: UUID
    quote_number: str
    quote_status: str
    policy_id: Optional[UUID] = None
    policy_number: Optional[str] = None
    policy_status: Optional[str] = None
    decision: str
    product_quote: ProductQuoteResponse
    document_status: str = "not_requested"
    documents: list[ProductPolicyDocumentItem] = Field(default_factory=list)
    idempotent: bool = False
