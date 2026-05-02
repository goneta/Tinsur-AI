"""
Focused tests for product-specific, versioned detail attachment models.

These tests intentionally avoid broad API fixtures. They validate that the new
records keep Quote, Policy, and Claim generic while attaching tenant-scoped,
product-versioned, schema-validated payloads as separate tables.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models import (
    Claim,
    Policy,
    ProductApplicationDetail,
    ProductClaimDetail,
    ProductRatingSnapshot,
    ProductVersion,
    Quote,
)
from app.schemas.product_application_detail import (
    ProductApplicationDetailCreate,
    ProductClaimDetailCreate,
    ProductRatingSnapshotCreate,
)


def test_product_specific_tables_are_versioned_and_tenant_scoped() -> None:
    assert ProductApplicationDetail.__tablename__ == "product_application_details"
    assert ProductRatingSnapshot.__tablename__ == "product_rating_snapshots"
    assert ProductClaimDetail.__tablename__ == "product_claim_details"

    for model, payload_column in (
        (ProductApplicationDetail, "application_data"),
        (ProductRatingSnapshot, "rating_data"),
        (ProductClaimDetail, "claim_data"),
    ):
        columns = model.__table__.columns
        assert "company_id" in columns
        assert "product_version_id" in columns
        assert "schema_version" in columns
        assert "validation_status" in columns
        assert "validation_errors" in columns
        assert payload_column in columns
        assert columns["company_id"].foreign_keys
        assert columns["product_version_id"].foreign_keys


def test_product_application_detail_schema_requires_versioned_payload_and_validation_errors() -> None:
    company_id = uuid4()
    quote_id = uuid4()
    product_version_id = uuid4()

    created = ProductApplicationDetailCreate(
        company_id=company_id,
        quote_id=quote_id,
        product_version_id=product_version_id,
        schema_version="car-application-v2",
        validation_schema_ref="product_quote_wizard_schemas:portal:car-application-v2",
        validation_status="valid",
        application_data={"vehicle": {"registration": "AB12 CDE"}, "driver": {"age": 35}},
    )

    assert created.schema_version == "car-application-v2"
    assert created.validation_schema_ref == "product_quote_wizard_schemas:portal:car-application-v2"
    assert created.application_data["vehicle"]["registration"] == "AB12 CDE"

    with pytest.raises(ValidationError):
        ProductApplicationDetailCreate(
            company_id=company_id,
            quote_id=quote_id,
            product_version_id=product_version_id,
            schema_version=" ",
            application_data={"vehicle": {"registration": "AB12 CDE"}},
        )

    with pytest.raises(ValidationError):
        ProductApplicationDetailCreate(
            company_id=company_id,
            quote_id=quote_id,
            product_version_id=product_version_id,
            validation_status="invalid",
            validation_errors=[],
            application_data={"vehicle": {"registration": "AB12 CDE"}},
        )

    with pytest.raises(ValidationError):
        ProductApplicationDetailCreate(
            company_id=company_id,
            quote_id=quote_id,
            product_version_id=product_version_id,
            application_data={},
        )


def test_product_rating_and_claim_detail_schemas_validate_payloads() -> None:
    company_id = uuid4()
    product_version_id = uuid4()

    rating_snapshot = ProductRatingSnapshotCreate(
        company_id=company_id,
        policy_id=uuid4(),
        product_version_id=product_version_id,
        schema_version="rating-v3",
        validation_status="valid",
        rating_data={
            "base_rate": "350.00",
            "factor_breakdown": [{"code": "ncd", "factor": "0.75"}],
            "bind_premium": "462.50",
        },
    )
    assert rating_snapshot.rating_data["factor_breakdown"][0]["code"] == "ncd"

    claim_detail = ProductClaimDetailCreate(
        company_id=company_id,
        claim_id=uuid4(),
        product_version_id=product_version_id,
        schema_version="motor-claim-v1",
        validation_status="invalid",
        validation_errors=[{"path": "vehicle.damage_photos", "message": "At least one photo is required"}],
        claim_data={"incident": {"type": "collision"}, "vehicle": {"driveable": False}},
    )
    assert claim_detail.validation_errors[0]["path"] == "vehicle.damage_photos"

    with pytest.raises(ValidationError):
        ProductRatingSnapshotCreate(
            company_id=company_id,
            policy_id=uuid4(),
            product_version_id=product_version_id,
            rating_data={},
        )

    with pytest.raises(ValidationError):
        ProductClaimDetailCreate(
            company_id=company_id,
            claim_id=uuid4(),
            product_version_id=product_version_id,
            claim_data={},
        )


def test_product_specific_details_attach_to_generic_core_records_without_changing_core_payloads() -> None:
    company_id = uuid4()
    client_id = uuid4()
    product_id = uuid4()
    product_version = ProductVersion(
        company_id=company_id,
        product_id=product_id,
        version="2026.05",
        status="active",
    )

    quote = Quote(
        company_id=company_id,
        client_id=client_id,
        quote_number="Q-PROD-001",
        premium_amount=Decimal("400.00"),
        final_premium=Decimal("460.00"),
        details={"legacy": "generic quote data remains available"},
    )
    application_detail = ProductApplicationDetail(
        company_id=company_id,
        quote=quote,
        product_version=product_version,
        schema_version="car-application-v2",
        application_data={"vehicle": {"registration": "AB12 CDE"}},
        validation_status="pending",
        validation_errors=[],
    )
    quote.product_application_detail = application_detail

    policy = Policy(
        company_id=company_id,
        client_id=client_id,
        quote=quote,
        policy_number="P-PROD-001",
        premium_amount=Decimal("460.00"),
        start_date=date(2026, 5, 1),
        end_date=date(2027, 4, 30),
        details={"legacy": "generic policy data remains available"},
    )
    rating_snapshot = ProductRatingSnapshot(
        company_id=company_id,
        policy=policy,
        product_version=product_version,
        schema_version="rating-v3",
        rating_data={"bind_premium": "460.00", "rating_engine": "factor_table"},
        validation_status="valid",
        validation_errors=[],
    )
    policy.product_rating_snapshot = rating_snapshot

    claim = Claim(
        company_id=company_id,
        client_id=client_id,
        policy=policy,
        claim_number="C-PROD-001",
        incident_date=date(2026, 6, 1),
        incident_description="Rear-end collision",
        claim_amount=Decimal("1200.00"),
    )
    claim_detail = ProductClaimDetail(
        company_id=company_id,
        claim=claim,
        product_version=product_version,
        schema_version="motor-claim-v1",
        claim_data={"damage": {"area": "rear bumper"}},
        validation_status="pending",
        validation_errors=[],
    )
    claim.product_claim_detail = claim_detail

    assert quote.details["legacy"] == "generic quote data remains available"
    assert quote.product_application_detail.application_data["vehicle"]["registration"] == "AB12 CDE"
    assert policy.details["legacy"] == "generic policy data remains available"
    assert policy.product_rating_snapshot.rating_data["rating_engine"] == "factor_table"
    assert claim.product_claim_detail.claim_data["damage"]["area"] == "rear bumper"
    assert product_version.application_details == [application_detail]
    assert product_version.rating_snapshots == [rating_snapshot]
    assert product_version.claim_details == [claim_detail]


def test_validation_status_helpers_preserve_structured_error_details() -> None:
    detail = ProductClaimDetail(
        company_id=uuid4(),
        claim_id=uuid4(),
        product_version_id=uuid4(),
        schema_version="motor-claim-v1",
        claim_data={"incident": {"type": "collision"}},
    )

    detail.mark_invalid([{"path": "incident.police_report", "message": "Police report required"}])
    assert detail.validation_status == "invalid"
    assert detail.validation_errors[0]["path"] == "incident.police_report"

    detail.mark_validated()
    assert detail.validation_status == "valid"
    assert detail.validation_errors == []
