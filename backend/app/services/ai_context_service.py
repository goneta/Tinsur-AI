"""
Tenant-scoped AI database context helpers.

This module builds compact, prompt-safe summaries from insurance records so
quote, policy, and orchestration agents can answer from live company data while
preserving the company_id tenant boundary on every query.
"""
from __future__ import annotations

import json
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.client import Client, client_company
from app.models.policy import Policy
from app.models.premium_policy import PremiumPolicyType
from app.models.product_catalog import InsuranceProduct, ProductVersion, CoverageDefinition
from app.models.quote import Quote


MAX_QUOTES = 20
MAX_POLICIES = 20
MAX_CLIENTS = 20
MAX_POLICY_TYPES = 20
MAX_PRODUCT_CATALOG_ITEMS = 20


def _coerce_uuid(value: Any) -> Optional[uuid.UUID]:
    """Return a UUID instance when value is a valid UUID-like object."""
    if not value:
        return None
    try:
        return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
    except (TypeError, ValueError, AttributeError):
        return None


def _safe_scalar(value: Any) -> Any:
    """Convert ORM scalar values into compact JSON-serialisable values."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    return value


def _compact_text(value: Any, limit: int = 180) -> Optional[str]:
    """Return a short one-line string or None for blank values."""
    if value is None:
        return None
    text = " ".join(str(value).split())
    if not text:
        return None
    return text[:limit]


def _client_name(client: Optional[Client]) -> str:
    if not client:
        return "Unknown"
    return client.display_name or client.email or "Unknown"


def _summarise_quote(quote: Quote) -> dict[str, Any]:
    details = quote.details or {}
    vehicle = details.get("vehicle") if isinstance(details, dict) else None
    if isinstance(vehicle, dict):
        vehicle_summary = {
            key: _safe_scalar(vehicle.get(key))
            for key in ("make", "model", "year", "registration_number", "usage")
            if vehicle.get(key) not in (None, "")
        }
    else:
        vehicle_summary = None

    return {
        "quote_number": quote.quote_number,
        "status": quote.status,
        "client": _client_name(quote.client),
        "policy_type": quote.policy_type.name if quote.policy_type else None,
        "coverage_amount": _safe_scalar(quote.coverage_amount),
        "premium_amount": _safe_scalar(quote.premium_amount),
        "final_premium": _safe_scalar(quote.final_premium),
        "premium_frequency": quote.premium_frequency,
        "valid_until": _safe_scalar(quote.valid_until),
        "created_at": _safe_scalar(quote.created_at),
        "vehicle": vehicle_summary,
    }


def _summarise_policy(policy: Policy) -> dict[str, Any]:
    return {
        "policy_number": policy.policy_number,
        "status": policy.status,
        "client": _client_name(policy.client),
        "policy_type": policy.policy_type.name if policy.policy_type else None,
        "premium_amount": _safe_scalar(policy.premium_amount),
        "coverage_amount": _safe_scalar(policy.coverage_amount),
        "premium_frequency": policy.premium_frequency,
        "start_date": _safe_scalar(policy.start_date),
        "end_date": _safe_scalar(policy.end_date),
        "auto_renew": policy.auto_renew,
    }


def _summarise_client(client: Client) -> dict[str, Any]:
    return {
        "name": client.display_name,
        "client_type": client.client_type,
        "email": client.email,
        "status": client.status,
        "kyc_status": client.kyc_status,
        "risk_profile": client.risk_profile,
        "no_claims_years": client.no_claims_years,
        "accident_count": client.accident_count,
        "number_of_accidents_at_fault": client.number_of_accidents_at_fault,
        "driving_license_years": client.driving_license_years,
    }


def _summarise_policy_type(policy_type: PremiumPolicyType) -> dict[str, Any]:
    return {
        "name": policy_type.name,
        "description": _compact_text(policy_type.description),
        "price": _safe_scalar(policy_type.price),
        "excess": _safe_scalar(policy_type.excess),
        "tagline": policy_type.tagline,
        "is_featured": policy_type.is_featured,
        "criteria_count": len(policy_type.criteria or []),
        "included_services": [service.name for service in (policy_type.services or []) if getattr(service, "name", None)],
    }


def _select_active_product_version(product: InsuranceProduct) -> Optional[ProductVersion]:
    versions = list(product.versions or [])
    active_versions = [version for version in versions if version.status == "active"]
    candidates = active_versions or versions
    if not candidates:
        return None
    return sorted(candidates, key=lambda version: version.created_at or datetime.min, reverse=True)[0]


def _summarise_product_catalog(product: InsuranceProduct) -> dict[str, Any]:
    active_version = _select_active_product_version(product)
    coverages = list(active_version.coverages or []) if active_version else []
    return {
        "code": product.code,
        "name": product.name,
        "product_line": product.product_line,
        "description": _compact_text(product.description),
        "active_version": active_version.version if active_version else None,
        "base_rate": _safe_scalar(active_version.base_rate) if active_version else None,
        "minimum_premium": _safe_scalar(active_version.minimum_premium) if active_version else None,
        "rating_strategy": active_version.rating_strategy if active_version else None,
        "coverages": [
            {
                "code": coverage.code,
                "name": coverage.name,
                "type": coverage.coverage_type,
                "required": coverage.is_required,
                "default_limit": _safe_scalar(coverage.default_limit),
                "option_count": len(coverage.options or []),
            }
            for coverage in sorted(coverages, key=lambda item: item.display_order or 100)
            if coverage.is_active
        ],
        "rating_factor_count": len(active_version.rating_factors or []) if active_version else 0,
        "underwriting_rule_count": len(active_version.underwriting_rules or []) if active_version else 0,
        "wizard_channels": [schema.channel for schema in (active_version.wizard_schemas or []) if schema.is_active] if active_version else [],
    }


def build_tenant_context_payload(db: Session, company_id: Any) -> dict[str, Any]:
    """
    Build a JSON-serialisable tenant context payload for AI agents.

    Every query is scoped by company_id, which is the multi-tenant isolation
    boundary for this platform. Invalid or missing company IDs return an empty
    payload rather than falling back to unscoped database reads.
    """
    company_uuid = _coerce_uuid(company_id)
    if not company_uuid:
        return {
            "tenant_scope": {"company_id": None, "is_scoped": False},
            "warning": "Company context is missing or invalid; no database records were loaded.",
            "quotes": [],
            "policies": [],
            "clients": [],
            "premium_products": [],
            "product_catalog": [],
        }

    recent_quotes = (
        db.query(Quote)
        .options(joinedload(Quote.client), joinedload(Quote.policy_type))
        .filter(Quote.company_id == company_uuid)
        .filter(Quote.status.in_(["draft", "draft_from_client", "sent", "accepted", "policy_created", "recommended"]))
        .order_by(Quote.created_at.desc())
        .limit(MAX_QUOTES)
        .all()
    )

    active_policies = (
        db.query(Policy)
        .options(joinedload(Policy.client), joinedload(Policy.policy_type))
        .filter(Policy.company_id == company_uuid)
        .filter(Policy.status.in_(["pending_activation", "active", "suspended", "renewed"]))
        .order_by(Policy.created_at.desc())
        .limit(MAX_POLICIES)
        .all()
    )

    clients = (
        db.query(Client)
        .join(client_company, client_company.c.client_id == Client.id)
        .filter(client_company.c.company_id == company_uuid)
        .order_by(Client.created_at.desc())
        .limit(MAX_CLIENTS)
        .all()
    )

    premium_products = (
        db.query(PremiumPolicyType)
        .options(joinedload(PremiumPolicyType.criteria), joinedload(PremiumPolicyType.services))
        .filter(PremiumPolicyType.company_id == company_uuid)
        .filter(PremiumPolicyType.is_active.is_(True))
        .order_by(PremiumPolicyType.is_featured.desc(), PremiumPolicyType.created_at.desc())
        .limit(MAX_POLICY_TYPES)
        .all()
    )

    product_catalog = (
        db.query(InsuranceProduct)
        .options(
            joinedload(InsuranceProduct.versions).joinedload(ProductVersion.coverages).joinedload(CoverageDefinition.options),
            joinedload(InsuranceProduct.versions).joinedload(ProductVersion.rating_factors),
            joinedload(InsuranceProduct.versions).joinedload(ProductVersion.underwriting_rules),
            joinedload(InsuranceProduct.versions).joinedload(ProductVersion.wizard_schemas),
        )
        .filter(InsuranceProduct.company_id == company_uuid)
        .filter(InsuranceProduct.is_active.is_(True))
        .order_by(InsuranceProduct.display_order.asc(), InsuranceProduct.name.asc())
        .limit(MAX_PRODUCT_CATALOG_ITEMS)
        .all()
    )

    return {
        "tenant_scope": {"company_id": str(company_uuid), "is_scoped": True},
        "record_counts": {
            "recent_quotes": len(recent_quotes),
            "active_policies": len(active_policies),
            "clients": len(clients),
            "premium_products": len(premium_products),
            "product_catalog": len(product_catalog),
        },
        "quotes": [_summarise_quote(quote) for quote in recent_quotes],
        "policies": [_summarise_policy(policy) for policy in active_policies],
        "clients": [_summarise_client(client) for client in clients],
        "premium_products": [_summarise_policy_type(policy_type) for policy_type in premium_products],
        "product_catalog": [_summarise_product_catalog(product) for product in product_catalog],
    }


def build_tenant_context_summary(db: Session, company_id: Any) -> str:
    """
    Build a compact system block that can be prepended to agent prompts.

    The summary is intentionally JSON formatted for model readability, but it is
    generated only after tenant-scoped ORM queries have executed.
    """
    payload = build_tenant_context_payload(db, company_id)
    return "[SYSTEM DATABASE CONTEXT - TENANT SCOPED]\n" + json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    )
