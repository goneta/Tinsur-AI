"""
Product catalog quote and recommendation engine for Milestone 5.

This service turns the Milestone 4 versioned catalog into deterministic customer
quote estimates. It evaluates active product versions, selected coverages,
coverage options, rating factors, taxes/fees, and underwriting rules for car,
travel, and home products without hard-coding a single product shape.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models.product_catalog import InsuranceProduct, ProductVersion
from app.schemas.product_catalog import ProductQuoteRecommendationRequest, ProductQuoteRequest

MONEY_QUANT = Decimal("0.01")


class ProductQuoteEngineService:
    """Rate and recommend active product-catalog products for a tenant."""

    def __init__(self, db: Session):
        self.db = db

    def calculate_quote(self, company_id: UUID, request: ProductQuoteRequest) -> dict[str, Any]:
        product = self._resolve_product(company_id, request)
        if not product:
            raise ValueError("No active product matched the quote request")
        version = self._active_version(product)
        if not version:
            raise ValueError("Product does not have an active version")
        return self._rate_product(product, version, request)

    def recommend_quotes(self, company_id: UUID, request: ProductQuoteRecommendationRequest) -> list[dict[str, Any]]:
        query = self._catalog_query(company_id)
        if request.product_line:
            query = query.filter(InsuranceProduct.product_line == request.product_line)
        products = query.order_by(InsuranceProduct.display_order.asc(), InsuranceProduct.name.asc()).all()

        recommendations: list[dict[str, Any]] = []
        for product in products:
            version = self._active_version(product)
            if not version:
                continue
            quote_request = ProductQuoteRequest(
                product_id=product.id,
                applicant_data=request.applicant_data,
                risk_data=request.risk_data,
                coverage_selections=request.coverage_selections,
                channel=request.channel,
                term_months=request.term_months,
            )
            quote = self._rate_product(product, version, quote_request)
            if quote["is_eligible"] or (request.include_referred and quote["referral_required"]):
                recommendations.append(quote)

        recommendations.sort(key=lambda item: (not item["is_eligible"], item["estimated_premium"], item["product_name"]))
        return recommendations

    def _catalog_query(self, company_id: UUID):
        return (
            self.db.query(InsuranceProduct)
            .options(
                joinedload(InsuranceProduct.versions).joinedload(ProductVersion.coverages),
                joinedload(InsuranceProduct.versions).joinedload(ProductVersion.rating_factors),
                joinedload(InsuranceProduct.versions).joinedload(ProductVersion.underwriting_rules),
                joinedload(InsuranceProduct.versions).joinedload(ProductVersion.wizard_schemas),
            )
            .filter(
                InsuranceProduct.company_id == company_id,
                InsuranceProduct.is_active.is_(True),
                InsuranceProduct.status == "active",
            )
        )

    def _resolve_product(self, company_id: UUID, request: ProductQuoteRequest) -> Optional[InsuranceProduct]:
        query = self._catalog_query(company_id)
        if request.product_id:
            return query.filter(InsuranceProduct.id == request.product_id).first()
        if request.product_code:
            return query.filter(InsuranceProduct.code == request.product_code).first()
        if request.product_line:
            return query.filter(InsuranceProduct.product_line == request.product_line).order_by(InsuranceProduct.display_order.asc()).first()
        return None

    @staticmethod
    def _active_version(product: InsuranceProduct) -> Optional[ProductVersion]:
        active_versions = [version for version in product.versions if version.status == "active"]
        if not active_versions:
            return None
        return sorted(active_versions, key=lambda item: item.effective_from or item.created_at, reverse=True)[0]

    def _rate_product(self, product: InsuranceProduct, version: ProductVersion, request: ProductQuoteRequest) -> dict[str, Any]:
        context = self._build_context(request)
        selected_coverages = {item.coverage_code: item for item in request.coverage_selections if item.is_selected}
        coverage_breakdown, coverage_multiplier, coverage_delta, coverage_reasons = self._evaluate_coverages(version, selected_coverages)
        underwriting_decisions = self._evaluate_underwriting(version, context)
        factor_breakdown, rating_multiplier, rating_amount = self._evaluate_rating_factors(version, context)

        rating_base = self._rating_base(version, context, coverage_breakdown)
        annualized_base = self._money(rating_base * self._decimal(version.base_rate or 0))
        term_factor = self._decimal(request.term_months) / Decimal("12")
        base_premium = self._money(max(annualized_base * term_factor, self._decimal(version.minimum_premium or 0) * term_factor))
        subtotal = self._money((base_premium * coverage_multiplier * rating_multiplier) + coverage_delta + rating_amount)
        if subtotal < Decimal("0"):
            subtotal = Decimal("0")
        taxes_and_fees, taxes_total = self._taxes_and_fees(version, subtotal)
        estimated = self._money(subtotal + taxes_total)

        declined = [item for item in underwriting_decisions if item["decision_effect"] == "decline"]
        referred = [item for item in underwriting_decisions if item["decision_effect"] == "refer"]
        if declined:
            decision = "declined"
        elif referred:
            decision = "refer"
        else:
            decision = "approved"

        wizard_schema = next((schema for schema in version.wizard_schemas if schema.is_active and schema.channel == request.channel), None)
        return {
            "product_id": product.id,
            "product_code": product.code,
            "product_name": product.name,
            "product_line": product.product_line,
            "product_version_id": version.id,
            "product_version": version.version,
            "currency": version.base_currency,
            "term_months": request.term_months,
            "rating_base": rating_base,
            "base_premium": base_premium,
            "subtotal_premium": subtotal,
            "taxes_and_fees_total": taxes_total,
            "estimated_premium": estimated,
            "is_eligible": not declined,
            "referral_required": bool(referred),
            "decision": decision,
            "decision_reasons": coverage_reasons + [item.get("message") or item["name"] for item in underwriting_decisions],
            "coverage_breakdown": coverage_breakdown,
            "factor_breakdown": factor_breakdown,
            "underwriting_decisions": underwriting_decisions,
            "taxes_and_fees": taxes_and_fees,
            "wizard_schema": wizard_schema,
        }

    @staticmethod
    def _build_context(request: ProductQuoteRequest) -> dict[str, Any]:
        context: dict[str, Any] = {}
        context.update(request.applicant_data or {})
        context.update(request.risk_data or {})
        context["applicant"] = request.applicant_data or {}
        context["risk"] = request.risk_data or {}
        context["term_months"] = request.term_months
        return context

    def _evaluate_coverages(self, version: ProductVersion, selected_coverages: dict[str, Any]) -> tuple[list[dict[str, Any]], Decimal, Decimal, list[str]]:
        breakdown: list[dict[str, Any]] = []
        multiplier = Decimal("1")
        delta = Decimal("0")
        reasons: list[str] = []
        for coverage in sorted([item for item in version.coverages if item.is_active], key=lambda item: item.display_order):
            selection = selected_coverages.get(coverage.code)
            if not coverage.is_required and not selection:
                continue
            option = None
            if selection and selection.option_code:
                option = next((item for item in coverage.options if item.code == selection.option_code and item.is_active), None)
                if not option:
                    reasons.append(f"Requested option {selection.option_code} is not available for {coverage.code}.")
            if option is None:
                option = next((item for item in coverage.options if item.is_default and item.is_active), None)
            limit_amount = self._decimal(getattr(selection, "limit_amount", None) or getattr(option, "limit_amount", None) or coverage.default_limit or 0)
            deductible_amount = self._decimal(getattr(selection, "deductible_amount", None) or getattr(option, "deductible_amount", None) or coverage.default_deductible or 0)
            if coverage.minimum_limit is not None and limit_amount and limit_amount < self._decimal(coverage.minimum_limit):
                reasons.append(f"{coverage.code} limit is below the configured minimum.")
            if coverage.maximum_limit is not None and limit_amount and limit_amount > self._decimal(coverage.maximum_limit):
                reasons.append(f"{coverage.code} limit is above the configured maximum and may require referral.")
            option_multiplier = self._decimal(getattr(option, "rate_multiplier", None) or 1)
            option_delta = self._decimal(getattr(option, "premium_delta", None) or 0)
            multiplier *= option_multiplier
            delta += option_delta
            breakdown.append({
                "coverage_code": coverage.code,
                "coverage_name": coverage.name,
                "option_code": getattr(option, "code", None),
                "option_label": getattr(option, "label", None),
                "limit_amount": limit_amount if limit_amount else None,
                "deductible_amount": deductible_amount if deductible_amount else None,
                "premium_delta": option_delta,
                "rate_multiplier": option_multiplier,
            })
        return breakdown, multiplier, delta, reasons

    def _evaluate_rating_factors(self, version: ProductVersion, context: dict[str, Any]) -> tuple[list[dict[str, Any]], Decimal, Decimal]:
        breakdown: list[dict[str, Any]] = []
        multiplier = Decimal("1")
        amount = Decimal("0")
        for factor in sorted([item for item in version.rating_factors if item.is_active], key=lambda item: item.priority):
            actual = self._get_path(context, factor.input_path)
            if not self._compare(actual, factor.operator, factor.value):
                continue
            factor_multiplier = self._decimal(factor.factor or 1)
            factor_amount = self._decimal(factor.amount or 0)
            if factor.factor_type in {"multiplier", "discount", "loading"}:
                multiplier *= factor_multiplier
            if factor.factor_type in {"amount", "fee", "discount", "loading"}:
                amount += factor_amount
            breakdown.append({
                "code": factor.code,
                "name": factor.name,
                "factor_type": factor.factor_type,
                "applies_to": factor.applies_to,
                "input_path": factor.input_path,
                "matched_value": actual,
                "factor": factor_multiplier,
                "amount": factor_amount,
                "reason_code": factor.reason_code,
            })
        return breakdown, multiplier, amount

    def _evaluate_underwriting(self, version: ProductVersion, context: dict[str, Any]) -> list[dict[str, Any]]:
        decisions: list[dict[str, Any]] = []
        for rule in sorted([item for item in version.underwriting_rules if item.is_active], key=lambda item: item.priority):
            condition = rule.condition or {}
            actual = self._get_path(context, condition.get("path", ""))
            if self._compare(actual, condition.get("operator", "equals"), condition.get("value")):
                decisions.append({
                    "code": rule.code,
                    "name": rule.name,
                    "decision_effect": rule.decision_effect,
                    "message": rule.message,
                    "authority_level": rule.authority_level,
                })
        return decisions

    def _rating_base(self, version: ProductVersion, context: dict[str, Any], coverage_breakdown: list[dict[str, Any]]) -> Decimal:
        config = version.configuration or {}
        base_path = config.get("rating_base")
        if base_path == "building_value_plus_contents":
            value = self._decimal(self._get_path(context, "property.building_value") or 0) + self._decimal(self._get_path(context, "property.contents_value") or 0)
        elif base_path:
            value = self._decimal(self._get_path(context, base_path) or 0)
        else:
            value = Decimal("0")
        if value <= 0:
            value = sum((self._decimal(item.get("limit_amount") or 0) for item in coverage_breakdown), Decimal("0"))
        return self._money(value)

    def _taxes_and_fees(self, version: ProductVersion, subtotal: Decimal) -> tuple[list[dict[str, Any]], Decimal]:
        items: list[dict[str, Any]] = []
        total = Decimal("0")
        for fee in version.taxes_and_fees or []:
            fee_type = fee.get("type", "fixed")
            if fee_type in {"percent", "percentage", "rate"}:
                amount = self._money(subtotal * self._decimal(fee.get("rate", fee.get("amount", 0))))
            else:
                amount = self._money(self._decimal(fee.get("amount", 0)))
            total += amount
            items.append({"code": fee.get("code", "fee"), "name": fee.get("name"), "fee_type": fee_type, "amount": amount})
        return items, self._money(total)

    @staticmethod
    def _get_path(data: dict[str, Any], path: str) -> Any:
        if not path:
            return None
        current: Any = data
        for part in path.split("."):
            if isinstance(current, dict):
                current = current.get(part)
            else:
                current = getattr(current, part, None)
            if current is None:
                return None
        return current

    def _compare(self, actual: Any, operator: str, expected: Any) -> bool:
        operator = (operator or "equals").lower()
        if operator == "exists":
            return actual is not None
        if operator in {"in", "not_in"}:
            expected_values = expected if isinstance(expected, list) else [item.strip() for item in str(expected).split(",")]
            result = str(actual) in {str(item) for item in expected_values}
            return not result if operator == "not_in" else result
        if operator == "between":
            values = expected if isinstance(expected, list) else [item.strip() for item in str(expected).split(",")]
            if len(values) != 2:
                return False
            actual_num = self._decimal(actual)
            return self._decimal(values[0]) <= actual_num <= self._decimal(values[1])
        if operator in {"gt", "gte", "lt", "lte", ">", ">=", "<", "<="}:
            actual_num = self._decimal(actual)
            expected_num = self._decimal(expected)
            return {
                "gt": actual_num > expected_num,
                ">": actual_num > expected_num,
                "gte": actual_num >= expected_num,
                ">=": actual_num >= expected_num,
                "lt": actual_num < expected_num,
                "<": actual_num < expected_num,
                "lte": actual_num <= expected_num,
                "<=": actual_num <= expected_num,
            }[operator]
        if operator == "contains":
            return str(expected).lower() in str(actual).lower()
        result = str(actual).lower() == str(expected).lower()
        if operator in {"not_equals", "!=", "ne"}:
            return not result
        return result

    @staticmethod
    def _decimal(value: Any) -> Decimal:
        if value is None:
            return Decimal("0")
        if isinstance(value, Decimal):
            return value
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return Decimal("0")

    def _money(self, value: Any) -> Decimal:
        return self._decimal(value).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
