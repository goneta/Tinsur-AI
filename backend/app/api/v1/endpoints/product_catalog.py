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
def create_coverage(
    version_id: UUID,
    coverage_data: CoverageDefinitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a coverage definition for a product version."""
    _get_version_or_404(db, current_user.company_id, version_id)
    data = coverage_data.model_dump()
    options_data = data.pop("options", [])
    coverage = CoverageDefinition(company_id=current_user.company_id, product_version_id=version_id, **data)
    for option_data in options_data:
        coverage.options.append(CoverageOption(company_id=current_user.company_id, **option_data))
    db.add(coverage)
    db.commit()
    db.refresh(coverage)
    return coverage


@router.put("/coverages/{coverage_id}", response_model=CoverageDefinitionResponse)
def update_coverage(
    coverage_id: UUID,
    coverage_data: CoverageDefinitionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update a coverage definition."""
    coverage = _get_coverage_or_404(db, current_user.company_id, coverage_id)
    for field, value in coverage_data.model_dump(exclude_unset=True).items():
        setattr(coverage, field, value)
    db.commit()
    db.refresh(coverage)
    return coverage


@router.post("/coverages/{coverage_id}/options", response_model=CoverageOptionResponse, status_code=status.HTTP_201_CREATED)
def create_coverage_option(
    coverage_id: UUID,
    option_data: CoverageOptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a selectable limit, deductible, or extension option for a coverage."""
    _get_coverage_or_404(db, current_user.company_id, coverage_id)
    option = CoverageOption(company_id=current_user.company_id, coverage_id=coverage_id, **option_data.model_dump())
    db.add(option)
    db.commit()
    db.refresh(option)
    return option


@router.put("/coverage-options/{option_id}", response_model=CoverageOptionResponse)
def update_coverage_option(
    option_id: UUID,
    option_data: CoverageOptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update a coverage option."""
    option = db.query(CoverageOption).filter(CoverageOption.company_id == current_user.company_id, CoverageOption.id == option_id).first()
    if not option:
        raise HTTPException(status_code=404, detail="Coverage option not found")
    for field, value in option_data.model_dump(exclude_unset=True).items():
        setattr(option, field, value)
    db.commit()
    db.refresh(option)
    return option


@router.post("/versions/{version_id}/rating-factors", response_model=RatingFactorResponse, status_code=status.HTTP_201_CREATED)
def create_rating_factor(
    version_id: UUID,
    factor_data: RatingFactorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a rating factor for a product version."""
    _get_version_or_404(db, current_user.company_id, version_id)
    factor = RatingFactor(company_id=current_user.company_id, product_version_id=version_id, **factor_data.model_dump())
    db.add(factor)
    db.commit()
    db.refresh(factor)
    return factor


@router.put("/rating-factors/{factor_id}", response_model=RatingFactorResponse)
def update_rating_factor(
    factor_id: UUID,
    factor_data: RatingFactorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update a rating factor."""
    factor = db.query(RatingFactor).filter(RatingFactor.company_id == current_user.company_id, RatingFactor.id == factor_id).first()
    if not factor:
        raise HTTPException(status_code=404, detail="Rating factor not found")
    for field, value in factor_data.model_dump(exclude_unset=True).items():
        setattr(factor, field, value)
    db.commit()
    db.refresh(factor)
    return factor


@router.post("/versions/{version_id}/underwriting-rules", response_model=ProductUnderwritingRuleResponse, status_code=status.HTTP_201_CREATED)
def create_underwriting_rule(
    version_id: UUID,
    rule_data: ProductUnderwritingRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create an eligibility, referral, or decline rule for a product version."""
    _get_version_or_404(db, current_user.company_id, version_id)
    rule = ProductUnderwritingRule(company_id=current_user.company_id, product_version_id=version_id, **rule_data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.put("/underwriting-rules/{rule_id}", response_model=ProductUnderwritingRuleResponse)
def update_underwriting_rule(
    rule_id: UUID,
    rule_data: ProductUnderwritingRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update a product-specific underwriting rule."""
    rule = db.query(ProductUnderwritingRule).filter(ProductUnderwritingRule.company_id == current_user.company_id, ProductUnderwritingRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Underwriting rule not found")
    for field, value in rule_data.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    db.commit()
    db.refresh(rule)
    return rule


@router.post("/versions/{version_id}/wizard-schemas", response_model=QuoteWizardSchemaResponse, status_code=status.HTTP_201_CREATED)
def create_wizard_schema(
    version_id: UUID,
    schema_data: QuoteWizardSchemaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a product-specific quote wizard schema for a channel such as portal or admin."""
    _get_version_or_404(db, current_user.company_id, version_id)
    wizard_schema = QuoteWizardSchema(company_id=current_user.company_id, product_version_id=version_id, **schema_data.model_dump())
    db.add(wizard_schema)
    db.commit()
    db.refresh(wizard_schema)
    return wizard_schema


@router.put("/wizard-schemas/{schema_id}", response_model=QuoteWizardSchemaResponse)
def update_wizard_schema(
    schema_id: UUID,
    schema_data: QuoteWizardSchemaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update a quote wizard schema."""
    wizard_schema = db.query(QuoteWizardSchema).filter(QuoteWizardSchema.company_id == current_user.company_id, QuoteWizardSchema.id == schema_id).first()
    if not wizard_schema:
        raise HTTPException(status_code=404, detail="Wizard schema not found")
    for field, value in schema_data.model_dump(exclude_unset=True).items():
        setattr(wizard_schema, field, value)
    db.commit()
    db.refresh(wizard_schema)
    return wizard_schema
