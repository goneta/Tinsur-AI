from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from app.schemas.product_catalog import ProductQuoteCoverageSelection, ProductQuoteRequest
from app.services.product_quote_engine_service import ProductQuoteEngineService


def _option(code, label, default=False, multiplier="1", delta="0", limit="0", deductible="0"):
    return SimpleNamespace(
        code=code,
        label=label,
        is_default=default,
        is_active=True,
        rate_multiplier=Decimal(multiplier),
        premium_delta=Decimal(delta),
        limit_amount=Decimal(limit),
        deductible_amount=Decimal(deductible),
    )


def _coverage(code, required=True, options=None, default_limit="0", min_limit=None, max_limit=None):
    return SimpleNamespace(
        code=code,
        name=code.replace("_", " ").title(),
        is_required=required,
        is_active=True,
        display_order=1,
        options=options or [],
        default_limit=Decimal(default_limit),
        default_deductible=Decimal("0"),
        minimum_limit=Decimal(min_limit) if min_limit else None,
        maximum_limit=Decimal(max_limit) if max_limit else None,
    )


def _factor(code, path, operator, value, multiplier="1", amount="0"):
    return SimpleNamespace(
        code=code,
        name=code.replace("_", " ").title(),
        factor_type="loading",
        applies_to="premium",
        input_path=path,
        operator=operator,
        value=value,
        factor=Decimal(multiplier),
        amount=Decimal(amount),
        reason_code=code.upper(),
        is_active=True,
        priority=1,
    )


def _rule(code, path, operator, value, effect="decline"):
    return SimpleNamespace(
        code=code,
        name=code.replace("_", " ").title(),
        condition={"path": path, "operator": operator, "value": value},
        decision_effect=effect,
        message=f"{code} triggered",
        authority_level="system",
        is_active=True,
        priority=1,
    )


def _version(**overrides):
    defaults = {
        "id": uuid4(),
        "version": "2026.1",
        "status": "active",
        "base_currency": "USD",
        "base_rate": Decimal("0.05"),
        "minimum_premium": Decimal("300"),
        "configuration": {"rating_base": "vehicle.market_value"},
        "coverages": [],
        "rating_factors": [],
        "underwriting_rules": [],
        "wizard_schemas": [],
        "taxes_and_fees": [{"code": "ipt", "name": "Insurance Premium Tax", "type": "percent", "rate": "0.10"}],
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _product(**overrides):
    defaults = {
        "id": uuid4(),
        "code": "CAR_STANDARD",
        "name": "Car Standard",
        "product_line": "car",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def test_product_quote_engine_rates_selected_coverage_options_and_factors():
    version = _version(
        coverages=[
            _coverage(
                "collision",
                required=True,
                options=[
                    _option("standard", "Standard", default=True, multiplier="1", delta="0", limit="20000"),
                    _option("enhanced", "Enhanced", multiplier="1.15", delta="50", limit="25000", deductible="250"),
                ],
            )
        ],
        rating_factors=[_factor("young_driver", "driver.age", "lt", 25, multiplier="1.20")],
    )
    request = ProductQuoteRequest(
        product_code="CAR_STANDARD",
        risk_data={"vehicle": {"market_value": 20000}, "driver": {"age": 22}},
        coverage_selections=[ProductQuoteCoverageSelection(coverage_code="collision", option_code="enhanced")],
    )

    quote = ProductQuoteEngineService(db=None)._rate_product(_product(), version, request)

    assert quote["rating_base"] == Decimal("20000.00")
    assert quote["base_premium"] == Decimal("1000.00")
    assert quote["subtotal_premium"] == Decimal("1430.00")
    assert quote["taxes_and_fees_total"] == Decimal("143.00")
    assert quote["estimated_premium"] == Decimal("1573.00")
    assert quote["decision"] == "approved"
    assert quote["coverage_breakdown"][0]["option_code"] == "enhanced"
    assert quote["factor_breakdown"][0]["code"] == "young_driver"


def test_product_quote_engine_declines_ineligible_risks_from_catalog_rules():
    version = _version(
        underwriting_rules=[_rule("unsafe_driver", "driver.accident_count", "gte", 4, effect="decline")]
    )
    request = ProductQuoteRequest(
        product_code="CAR_STANDARD",
        risk_data={"vehicle": {"market_value": 20000}, "driver": {"accident_count": 4}},
    )

    quote = ProductQuoteEngineService(db=None)._rate_product(_product(), version, request)

    assert quote["is_eligible"] is False
    assert quote["decision"] == "declined"
    assert quote["underwriting_decisions"][0]["code"] == "unsafe_driver"


def test_product_quote_engine_supports_home_rating_base_composition():
    version = _version(
        configuration={"rating_base": "building_value_plus_contents"},
        base_rate=Decimal("0.002"),
        minimum_premium=Decimal("100"),
        taxes_and_fees=[],
    )
    request = ProductQuoteRequest(
        product_code="HOME_STANDARD",
        risk_data={"property": {"building_value": 250000, "contents_value": 50000}},
    )

    quote = ProductQuoteEngineService(db=None)._rate_product(_product(code="HOME_STANDARD", name="Home Standard", product_line="home"), version, request)

    assert quote["rating_base"] == Decimal("300000.00")
    assert quote["base_premium"] == Decimal("600.00")
    assert quote["estimated_premium"] == Decimal("600.00")
