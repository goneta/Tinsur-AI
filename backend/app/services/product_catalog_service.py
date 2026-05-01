"""
Product catalog service for Milestone 4.

The service centralises nested product-version creation, seeded catalog defaults,
and compact summaries that can be reused by API endpoints, quote flows, and AI
context assembly without duplicating tenant-scoped query logic.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Iterable, Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models.product_catalog import (
    CoverageDefinition,
    CoverageOption,
    InsuranceProduct,
    ProductUnderwritingRule,
    ProductVersion,
    QuoteWizardSchema,
    RatingFactor,
)
from app.schemas.product_catalog import InsuranceProductCreate, ProductVersionCreate


DEFAULT_PRODUCT_CATALOG: list[dict[str, Any]] = [
    {
        "code": "CAR-COMP",
        "name": "Comprehensive Car Insurance",
        "product_line": "car",
        "description": "Automatic car insurance for private vehicles using driver, vehicle, usage, claims, and cover selections.",
        "display_order": 10,
        "metadata_json": {"recommended_for": ["private_car", "family_car"], "issuance_mode": "automatic_after_underwriting"},
        "versions": [
            {
                "version": "2026.1",
                "status": "active",
                "base_currency": "USD",
                "rating_strategy": "factor_table",
                "base_rate": Decimal("0.0475"),
                "minimum_premium": Decimal("250"),
                "taxes_and_fees": [{"code": "admin_fee", "type": "fixed", "amount": 25}],
                "configuration": {"rating_base": "vehicle.market_value", "term_months": 12},
                "coverages": [
                    {
                        "code": "OWN_DAMAGE",
                        "name": "Own Damage",
                        "coverage_type": "core",
                        "description": "Repairs or replaces the insured vehicle after accidental damage, fire, or theft.",
                        "is_required": True,
                        "default_limit": Decimal("25000"),
                        "minimum_limit": Decimal("5000"),
                        "maximum_limit": Decimal("150000"),
                        "default_deductible": Decimal("500"),
                        "options": [
                            {"code": "STD_EXCESS", "label": "Standard excess", "deductible_amount": Decimal("500"), "rate_multiplier": Decimal("1"), "is_default": True},
                            {"code": "LOW_EXCESS", "label": "Low excess", "deductible_amount": Decimal("250"), "rate_multiplier": Decimal("1.08")},
                        ],
                    },
                    {
                        "code": "THIRD_PARTY",
                        "name": "Third Party Liability",
                        "coverage_type": "liability",
                        "description": "Covers injury or property damage caused to others by the insured vehicle.",
                        "is_required": True,
                        "default_limit": Decimal("1000000"),
                        "minimum_limit": Decimal("500000"),
                        "maximum_limit": Decimal("5000000"),
                        "options": [
                            {"code": "LIAB_1M", "label": "1,000,000 liability limit", "limit_amount": Decimal("1000000"), "is_default": True},
                            {"code": "LIAB_5M", "label": "5,000,000 liability limit", "limit_amount": Decimal("5000000"), "rate_multiplier": Decimal("1.15")},
                        ],
                    },
                    {
                        "code": "ROADSIDE",
                        "name": "Roadside Assistance",
                        "coverage_type": "optional_extension",
                        "description": "Towing, emergency assistance, and roadside support.",
                        "premium_delta": Decimal("0") if False else None,
                        "is_required": False,
                        "options": [
                            {"code": "ROADSIDE_BASIC", "label": "Roadside basic", "premium_delta": Decimal("35"), "is_default": True},
                            {"code": "ROADSIDE_PLUS", "label": "Roadside plus", "premium_delta": Decimal("65")},
                        ],
                    },
                ],
                "rating_factors": [
                    {"code": "YOUNG_DRIVER", "name": "Young primary driver", "factor_type": "multiplier", "applies_to": "driver", "input_path": "drivers.primary.age", "operator": "lt", "value": "25", "factor": Decimal("1.25"), "reason_code": "AGE_UNDER_25", "priority": 10},
                    {"code": "HIGH_VALUE", "name": "High vehicle value", "factor_type": "multiplier", "applies_to": "vehicle", "input_path": "vehicle.market_value", "operator": "gt", "value": "75000", "factor": Decimal("1.18"), "reason_code": "HIGH_VALUE_VEHICLE", "priority": 20},
                    {"code": "NO_CLAIMS", "name": "No claims discount", "factor_type": "multiplier", "applies_to": "driver", "input_path": "drivers.primary.no_claim_discount_years", "operator": "gte", "value": "5", "factor": Decimal("0.82"), "reason_code": "NCD_5_PLUS", "priority": 30},
                ],
                "underwriting_rules": [
                    {"code": "DECLINE_UNLICENSED", "name": "Decline unlicensed drivers", "decision_effect": "decline", "condition": {"path": "drivers.primary.years_licensed", "operator": "lt", "value": 1}, "message": "Primary driver must have at least one licensed year.", "priority": 5},
                    {"code": "REFER_HIGH_CLAIMS", "name": "Refer high claim frequency", "decision_effect": "refer", "condition": {"path": "drivers.primary.claim_count_3y", "operator": "gte", "value": 3}, "message": "Manual review required for three or more claims in three years.", "authority_level": "senior_underwriter", "priority": 15},
                ],
                "wizard_schemas": [
                    {
                        "channel": "portal",
                        "schema_version": "1.0",
                        "title": "Car insurance quote",
                        "steps": [
                            {"id": "driver", "title": "Driver details", "fields": ["first_name", "last_name", "date_of_birth", "years_licensed", "claims"]},
                            {"id": "vehicle", "title": "Car details", "fields": ["make", "model", "year", "market_value", "usage_class", "annual_mileage"]},
                            {"id": "cover", "title": "Coverage choices", "fields": ["excess", "liability_limit", "optional_extensions"]},
                        ],
                        "validation_schema": {"required": ["driver", "vehicle", "cover"]},
                    }
                ],
            }
        ],
    },
    {
        "code": "TRAVEL-SINGLE",
        "name": "Single Trip Travel Insurance",
        "product_line": "travel",
        "description": "Automatic trip protection using traveller ages, destination region, trip duration, medical disclosures, and optional baggage cover.",
        "display_order": 20,
        "metadata_json": {"recommended_for": ["leisure", "business_trip"], "issuance_mode": "automatic_after_screening"},
        "versions": [
            {
                "version": "2026.1",
                "status": "active",
                "base_currency": "USD",
                "rating_strategy": "factor_table",
                "base_rate": Decimal("0.018"),
                "minimum_premium": Decimal("35"),
                "configuration": {"rating_base": "trip_cost", "max_trip_days": 120},
                "coverages": [
                    {"code": "MEDICAL", "name": "Emergency Medical", "coverage_type": "core", "is_required": True, "default_limit": Decimal("250000"), "maximum_limit": Decimal("1000000"), "options": [{"code": "MED_250K", "label": "250,000 medical", "limit_amount": Decimal("250000"), "is_default": True}, {"code": "MED_1M", "label": "1,000,000 medical", "limit_amount": Decimal("1000000"), "rate_multiplier": Decimal("1.22")}]},
                    {"code": "CANCELLATION", "name": "Trip Cancellation", "coverage_type": "core", "is_required": True, "default_limit": Decimal("5000"), "maximum_limit": Decimal("25000"), "options": [{"code": "CANCEL_STD", "label": "Trip cost cancellation", "is_default": True}]},
                    {"code": "BAGGAGE", "name": "Baggage Protection", "coverage_type": "optional_extension", "is_required": False, "default_limit": Decimal("1500"), "options": [{"code": "BAG_1500", "label": "1,500 baggage", "premium_delta": Decimal("18"), "is_default": True}, {"code": "BAG_3000", "label": "3,000 baggage", "premium_delta": Decimal("32")}]},
                ],
                "rating_factors": [
                    {"code": "SENIOR_TRAVELLER", "name": "Senior traveller", "factor_type": "multiplier", "applies_to": "traveller", "input_path": "travellers.max_age", "operator": "gte", "value": "70", "factor": Decimal("1.55"), "reason_code": "AGE_70_PLUS", "priority": 10},
                    {"code": "LONG_TRIP", "name": "Long trip duration", "factor_type": "multiplier", "applies_to": "trip", "input_path": "trip.duration_days", "operator": "gt", "value": "30", "factor": Decimal("1.2"), "reason_code": "TRIP_OVER_30_DAYS", "priority": 20},
                ],
                "underwriting_rules": [
                    {"code": "DECLINE_SANCTIONED_DESTINATION", "name": "Decline restricted destinations", "decision_effect": "decline", "condition": {"path": "trip.destination_risk", "operator": "equals", "value": "restricted"}, "message": "Destination is outside current underwriting appetite.", "priority": 5},
                    {"code": "REFER_MEDICAL_DISCLOSURE", "name": "Refer medical disclosures", "decision_effect": "refer", "condition": {"path": "travellers.has_medical_disclosure", "operator": "equals", "value": True}, "message": "Medical disclosure requires review.", "authority_level": "medical_underwriter", "priority": 15},
                ],
                "wizard_schemas": [{"channel": "portal", "schema_version": "1.0", "title": "Travel insurance quote", "steps": [{"id": "trip", "title": "Trip details", "fields": ["destination", "departure_date", "return_date", "trip_cost"]}, {"id": "travellers", "title": "Traveller details", "fields": ["traveller_ages", "residency", "medical_disclosures"]}, {"id": "cover", "title": "Coverage choices", "fields": ["medical_limit", "cancellation_limit", "baggage"]}], "validation_schema": {"required": ["trip", "travellers"]}}],
            }
        ],
    },
    {
        "code": "HOME-COMP",
        "name": "Comprehensive Home Insurance",
        "product_line": "home",
        "description": "Automatic home insurance for buildings and contents using property details, occupancy, security, flood/fire risk, and coverage selections.",
        "display_order": 30,
        "metadata_json": {"recommended_for": ["owner_occupied", "mortgaged_home"], "issuance_mode": "automatic_after_property_screening"},
        "versions": [
            {
                "version": "2026.1",
                "status": "active",
                "base_currency": "USD",
                "rating_strategy": "factor_table",
                "base_rate": Decimal("0.0035"),
                "minimum_premium": Decimal("180"),
                "configuration": {"rating_base": "building_value_plus_contents", "term_months": 12},
                "coverages": [
                    {"code": "BUILDINGS", "name": "Buildings Cover", "coverage_type": "core", "is_required": True, "default_limit": Decimal("250000"), "maximum_limit": Decimal("2000000"), "default_deductible": Decimal("1000"), "options": [{"code": "BLD_STD", "label": "Standard buildings cover", "deductible_amount": Decimal("1000"), "is_default": True}]},
                    {"code": "CONTENTS", "name": "Contents Cover", "coverage_type": "core", "is_required": True, "default_limit": Decimal("50000"), "maximum_limit": Decimal("250000"), "default_deductible": Decimal("500"), "options": [{"code": "CONT_50K", "label": "50,000 contents", "limit_amount": Decimal("50000"), "is_default": True}, {"code": "CONT_100K", "label": "100,000 contents", "limit_amount": Decimal("100000"), "rate_multiplier": Decimal("1.12")}]},
                    {"code": "PERSONAL_POSSESSIONS", "name": "Personal Possessions", "coverage_type": "optional_extension", "is_required": False, "default_limit": Decimal("5000"), "options": [{"code": "PP_5K", "label": "5,000 possessions", "premium_delta": Decimal("45"), "is_default": True}]},
                ],
                "rating_factors": [
                    {"code": "FLOOD_ZONE", "name": "Flood zone loading", "factor_type": "multiplier", "applies_to": "property", "input_path": "property.flood_risk", "operator": "equals", "value": "high", "factor": Decimal("1.4"), "reason_code": "HIGH_FLOOD_RISK", "priority": 10},
                    {"code": "SECURITY_DISCOUNT", "name": "Security device discount", "factor_type": "multiplier", "applies_to": "property", "input_path": "property.has_monitored_alarm", "operator": "equals", "value": "true", "factor": Decimal("0.92"), "reason_code": "MONITORED_ALARM", "priority": 20},
                ],
                "underwriting_rules": [
                    {"code": "REFER_UNOCCUPIED", "name": "Refer long unoccupied homes", "decision_effect": "refer", "condition": {"path": "property.unoccupied_days", "operator": "gt", "value": 60}, "message": "Homes unoccupied for more than 60 days require review.", "authority_level": "property_underwriter", "priority": 10},
                    {"code": "DECLINE_DERELICT", "name": "Decline derelict properties", "decision_effect": "decline", "condition": {"path": "property.condition", "operator": "equals", "value": "derelict"}, "message": "Derelict properties are outside appetite.", "priority": 5},
                ],
                "wizard_schemas": [{"channel": "portal", "schema_version": "1.0", "title": "Home insurance quote", "steps": [{"id": "property", "title": "Property details", "fields": ["address", "property_type", "construction_year", "building_value", "contents_value"]}, {"id": "risk", "title": "Risk details", "fields": ["occupancy", "security", "flood_risk", "fire_risk"]}, {"id": "cover", "title": "Coverage choices", "fields": ["building_cover", "contents_cover", "deductible"]}], "validation_schema": {"required": ["property", "risk"]}}],
            }
        ],
    },
]


class ProductCatalogService:
    """Tenant-scoped product catalog operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_product(self, company_id: UUID, payload: InsuranceProductCreate, created_by_id: Optional[UUID] = None) -> InsuranceProduct:
        data = payload.model_dump()
        versions_data = data.pop("versions", [])
        product = InsuranceProduct(company_id=company_id, **data)
        for version_payload in versions_data:
            product.versions.append(self._build_version(company_id, version_payload, created_by_id))
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def add_version(self, company_id: UUID, product: InsuranceProduct, payload: ProductVersionCreate, created_by_id: Optional[UUID] = None) -> ProductVersion:
        version = self._build_version(company_id, payload.model_dump(), created_by_id)
        product.versions.append(version)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(version)
        return version

    def seed_defaults(self, company_id: UUID, created_by_id: Optional[UUID] = None) -> tuple[list[InsuranceProduct], int, int]:
        products: list[InsuranceProduct] = []
        created = 0
        updated = 0
        for raw_product in DEFAULT_PRODUCT_CATALOG:
            existing = self.db.query(InsuranceProduct).filter(
                InsuranceProduct.company_id == company_id,
                InsuranceProduct.code == raw_product["code"],
            ).first()
            payload = InsuranceProductCreate(**raw_product)
            if existing:
                update_data = payload.model_dump(exclude={"versions"})
                for field, value in update_data.items():
                    setattr(existing, field, value)
                if not self._has_version(existing.versions, raw_product["versions"][0]["version"]):
                    existing.versions.append(self._build_version(company_id, raw_product["versions"][0], created_by_id))
                products.append(existing)
                updated += 1
            else:
                product_data = payload.model_dump()
                versions_data = product_data.pop("versions", [])
                product = InsuranceProduct(company_id=company_id, **product_data)
                for version_data in versions_data:
                    product.versions.append(self._build_version(company_id, version_data, created_by_id))
                self.db.add(product)
                products.append(product)
                created += 1
        self.db.commit()
        for product in products:
            self.db.refresh(product)
        return products, created, updated

    def list_products(self, company_id: UUID, product_line: Optional[str] = None, active_only: bool = False, page: int = 1, page_size: int = 50) -> tuple[list[InsuranceProduct], int]:
        query = self.db.query(InsuranceProduct).options(
            joinedload(InsuranceProduct.versions).joinedload(ProductVersion.coverages).joinedload(CoverageDefinition.options),
            joinedload(InsuranceProduct.versions).joinedload(ProductVersion.rating_factors),
            joinedload(InsuranceProduct.versions).joinedload(ProductVersion.underwriting_rules),
            joinedload(InsuranceProduct.versions).joinedload(ProductVersion.wizard_schemas),
        ).filter(InsuranceProduct.company_id == company_id)
        if product_line:
            query = query.filter(InsuranceProduct.product_line == product_line)
        if active_only:
            query = query.filter(InsuranceProduct.is_active.is_(True), InsuranceProduct.status == "active")
        total = query.count()
        items = query.order_by(InsuranceProduct.display_order.asc(), InsuranceProduct.name.asc()).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def get_product(self, company_id: UUID, product_id: UUID) -> Optional[InsuranceProduct]:
        return self.db.query(InsuranceProduct).options(
            joinedload(InsuranceProduct.versions).joinedload(ProductVersion.coverages).joinedload(CoverageDefinition.options),
            joinedload(InsuranceProduct.versions).joinedload(ProductVersion.rating_factors),
            joinedload(InsuranceProduct.versions).joinedload(ProductVersion.underwriting_rules),
            joinedload(InsuranceProduct.versions).joinedload(ProductVersion.wizard_schemas),
        ).filter(InsuranceProduct.company_id == company_id, InsuranceProduct.id == product_id).first()

    def get_active_catalog_summary(self, company_id: UUID) -> list[dict[str, Any]]:
        products, _ = self.list_products(company_id=company_id, active_only=True, page=1, page_size=100)
        summary: list[dict[str, Any]] = []
        for product in products:
            active_version = self._select_active_version(product.versions)
            summary.append({
                "product_id": product.id,
                "code": product.code,
                "name": product.name,
                "product_line": product.product_line,
                "active_version_id": active_version.id if active_version else None,
                "active_version": active_version.version if active_version else None,
                "coverage_count": len(active_version.coverages) if active_version else 0,
                "rating_factor_count": len(active_version.rating_factors) if active_version else 0,
                "underwriting_rule_count": len(active_version.underwriting_rules) if active_version else 0,
                "wizard_channels": [schema.channel for schema in (active_version.wizard_schemas if active_version else []) if schema.is_active],
            })
        return summary

    def _build_version(self, company_id: UUID, version_data: dict[str, Any], created_by_id: Optional[UUID]) -> ProductVersion:
        coverages_data = version_data.pop("coverages", [])
        rating_factors_data = version_data.pop("rating_factors", [])
        underwriting_rules_data = version_data.pop("underwriting_rules", [])
        wizard_schemas_data = version_data.pop("wizard_schemas", [])
        version = ProductVersion(company_id=company_id, created_by_id=created_by_id, **version_data)
        for coverage_data in coverages_data:
            options_data = coverage_data.pop("options", [])
            coverage = CoverageDefinition(company_id=company_id, **coverage_data)
            for option_data in options_data:
                coverage.options.append(CoverageOption(company_id=company_id, **option_data))
            version.coverages.append(coverage)
        for factor_data in rating_factors_data:
            version.rating_factors.append(RatingFactor(company_id=company_id, **factor_data))
        for rule_data in underwriting_rules_data:
            version.underwriting_rules.append(ProductUnderwritingRule(company_id=company_id, **rule_data))
        for schema_data in wizard_schemas_data:
            version.wizard_schemas.append(QuoteWizardSchema(company_id=company_id, **schema_data))
        return version

    @staticmethod
    def _has_version(versions: Iterable[ProductVersion], version_name: str) -> bool:
        return any(version.version == version_name for version in versions)

    @staticmethod
    def _select_active_version(versions: Iterable[ProductVersion]) -> Optional[ProductVersion]:
        active_versions = [version for version in versions if version.status == "active"]
        if active_versions:
            return sorted(active_versions, key=lambda item: item.created_at or 0, reverse=True)[0]
        available_versions = list(versions)
        return sorted(available_versions, key=lambda item: item.created_at or 0, reverse=True)[0] if available_versions else None
