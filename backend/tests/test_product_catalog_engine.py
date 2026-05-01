"""
Focused Milestone 4 validation for the product and coverage catalog engine.

These tests intentionally avoid the repository-wide SQLite fixture because several
legacy models use dialect-specific UUID columns. The Milestone 4 assertions focus
on schema validation, seeded catalog completeness, nested ORM construction, and
AI summarisation logic for product catalog awareness.
"""
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.product_catalog import InsuranceProductCreate, QuoteWizardSchemaCreate
from app.services.ai_context_service import _summarise_product_catalog
from app.services.product_catalog_service import DEFAULT_PRODUCT_CATALOG, ProductCatalogService


def test_default_product_catalog_contains_car_travel_home_definitions():
    products = [InsuranceProductCreate(**raw_product) for raw_product in DEFAULT_PRODUCT_CATALOG]

    assert {product.product_line for product in products} == {"car", "travel", "home"}
    assert {product.code for product in products} == {"CAR-COMP", "TRAVEL-SINGLE", "HOME-COMP"}
    for product in products:
        assert product.versions, f"{product.code} must include at least one version"
        active_version = product.versions[0]
        assert active_version.status == "active"
        assert active_version.coverages, f"{product.code} must define coverages"
        assert active_version.rating_factors, f"{product.code} must define rating factors"
        assert active_version.underwriting_rules, f"{product.code} must define underwriting rules"
        assert active_version.wizard_schemas, f"{product.code} must define quote wizard schemas"
        assert all(schema.steps for schema in active_version.wizard_schemas)


def test_nested_product_version_builder_creates_coverages_options_rules_and_wizards():
    company_id = uuid4()
    created_by_id = uuid4()
    product_payload = InsuranceProductCreate(**DEFAULT_PRODUCT_CATALOG[0])
    service = ProductCatalogService.__new__(ProductCatalogService)

    version = service._build_version(company_id, product_payload.versions[0].model_dump(), created_by_id)

    assert version.company_id == company_id
    assert version.created_by_id == created_by_id
    assert version.version == "2026.1"
    assert len(version.coverages) >= 3
    assert any(coverage.code == "OWN_DAMAGE" and coverage.options for coverage in version.coverages)
    assert {factor.code for factor in version.rating_factors} >= {"YOUNG_DRIVER", "NO_CLAIMS"}
    assert {rule.decision_effect for rule in version.underwriting_rules} >= {"decline", "refer"}
    assert version.wizard_schemas[0].channel == "portal"


def test_ai_context_product_catalog_summary_shape():
    coverage = SimpleNamespace(
        code="OWN_DAMAGE",
        name="Own Damage",
        coverage_type="core",
        is_required=True,
        default_limit=25000,
        options=[SimpleNamespace(code="STD_EXCESS")],
        display_order=10,
        is_active=True,
    )
    version = SimpleNamespace(
        status="active",
        version="2026.1",
        created_at=None,
        base_rate=0.0475,
        minimum_premium=250,
        rating_strategy="factor_table",
        coverages=[coverage],
        rating_factors=[SimpleNamespace(code="YOUNG_DRIVER")],
        underwriting_rules=[SimpleNamespace(code="DECLINE_UNLICENSED")],
        wizard_schemas=[SimpleNamespace(channel="portal", is_active=True)],
    )
    product = SimpleNamespace(
        code="CAR-COMP",
        name="Comprehensive Car Insurance",
        product_line="car",
        description="Automatic car insurance using driver and vehicle details.",
        versions=[version],
    )

    summary = _summarise_product_catalog(product)

    assert summary["code"] == "CAR-COMP"
    assert summary["product_line"] == "car"
    assert summary["active_version"] == "2026.1"
    assert summary["coverages"][0]["code"] == "OWN_DAMAGE"
    assert summary["rating_factor_count"] == 1
    assert summary["underwriting_rule_count"] == 1
    assert summary["wizard_channels"] == ["portal"]


def test_quote_wizard_schema_requires_steps():
    with pytest.raises(ValidationError, match="at least one step"):
        QuoteWizardSchemaCreate(title="Invalid wizard", steps=[])
