from uuid import uuid4

from app.schemas.underwriting_intake import StructuredQuoteIntakeRequest
from app.services.underwriting_service import UnderwritingService


class QueryStub:
    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return None


class DBStub:
    def query(self, *args, **kwargs):
        return QueryStub()


def test_deterministic_structured_underwriting_accepts_clean_private_vehicle():
    payload = {
        "client": {"client_id": uuid4(), "consent_to_underwrite": True},
        "vehicle": {
            "make": "Toyota",
            "model": "Corolla",
            "year": 2021,
            "market_value": "18000.00",
            "usage_class": "private",
            "annual_mileage": 9000,
        },
        "drivers": [
            {
                "first_name": "Jane",
                "last_name": "Driver",
                "date_of_birth": "1988-04-12",
                "years_licensed": 12,
                "is_primary": True,
            }
        ],
        "usage": {"policy_duration_months": 12, "use_class": "private"},
        "cover_options": {
            "policy_type_id": uuid4(),
            "coverage_amount": "18000.00",
            "cover_level": "comprehensive",
        },
        "ncd": {"years": 5, "proof_available": True},
        "payment_terms": {"premium_frequency": "annual"},
    }

    request = StructuredQuoteIntakeRequest.model_validate(payload)
    result = UnderwritingService(DBStub()).deterministic_quote_underwriting(
        company_id=uuid4(),
        intake=request.model_dump(mode="python"),
        persist=False,
    )

    assert result["decision"] == "accept"
    assert str(result["final_premium"]) == "648.00"
    assert str(result["risk_score"]) == "20.00"
    assert result["normalized_payload"]["vehicle"]["make"] == "Toyota"
    assert result["normalized_payload"]["drivers"][0]["is_primary"] is True
    assert result["decline_reasons"] == []
