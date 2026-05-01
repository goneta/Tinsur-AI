import asyncio
import sys
from datetime import date, timedelta
from decimal import Decimal
from types import ModuleType, SimpleNamespace
from uuid import uuid4

from app.core.time import utcnow
from app.models.client import Client, client_company
from app.models.policy import Policy
from app.models.premium_policy import PremiumPolicyType
from app.models.quote import Quote
from app.models.user import User
from app.services.ai_context_service import build_tenant_context_payload, build_tenant_context_summary


class QueryDouble:
    def __init__(self, rows):
        self.rows = list(rows)
        self.filters = []
        self.joins = []
        self.limit_value = None

    def options(self, *args, **kwargs):
        return self

    def join(self, *args, **kwargs):
        self.joins.extend(args)
        return self

    def filter(self, *criteria):
        self.filters.extend(criteria)
        return self

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def all(self):
        return self.rows[: self.limit_value] if self.limit_value else self.rows

    def first(self):
        return self.rows[0] if self.rows else None


class DatabaseDouble:
    def __init__(self, rows_by_model):
        self.rows_by_model = rows_by_model
        self.queries = []

    def query(self, model):
        query = QueryDouble(self.rows_by_model.get(model, []))
        self.queries.append((model, query))
        return query


def _client(name: str, email: str = "driver@example.com"):
    return SimpleNamespace(
        id=uuid4(),
        display_name=name,
        client_type="individual",
        email=email,
        status="active",
        kyc_status="verified",
        risk_profile="low",
        no_claims_years=4,
        accident_count=0,
        number_of_accidents_at_fault=0,
        driving_license_years=7,
        first_name=name.split()[0],
        last_name=name.split()[-1],
    )


def _policy_type(name: str):
    return SimpleNamespace(
        id=uuid4(),
        name=name,
        description=f"{name} cover",
        price=Decimal("400.00"),
        excess=Decimal("100.00"),
        tagline="Fast automatic protection",
        is_featured=True,
        is_active=True,
        criteria=[],
        services=[],
        created_at=utcnow(),
    )


def test_tenant_context_summary_uses_company_scoped_queries_and_records():
    company_id = uuid4()
    client = _client("Alice Driver")
    product = _policy_type("Alpha Auto Plus")
    quote = SimpleNamespace(
        quote_number="QA-1001",
        status="draft",
        client=client,
        policy_type=product,
        coverage_amount=Decimal("10000.00"),
        premium_amount=Decimal("450.00"),
        final_premium=Decimal("475.00"),
        premium_frequency="monthly",
        valid_until=date.today() + timedelta(days=30),
        created_at=utcnow(),
        details={"vehicle": {"make": "Toyota", "model": "Corolla", "year": 2022}},
    )
    policy = SimpleNamespace(
        policy_number="PA-1001",
        status="active",
        client=client,
        policy_type=product,
        premium_amount=Decimal("475.00"),
        coverage_amount=Decimal("10000.00"),
        premium_frequency="monthly",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        auto_renew=True,
        created_at=utcnow(),
    )
    db = DatabaseDouble({Quote: [quote], Policy: [policy], Client: [client], PremiumPolicyType: [product]})

    payload = build_tenant_context_payload(db, company_id)
    summary = build_tenant_context_summary(db, company_id)

    assert payload["tenant_scope"] == {"company_id": str(company_id), "is_scoped": True}
    assert payload["record_counts"] == {
        "recent_quotes": 1,
        "active_policies": 1,
        "clients": 1,
        "premium_products": 1,
    }
    assert payload["quotes"][0]["quote_number"] == "QA-1001"
    assert payload["policies"][0]["policy_number"] == "PA-1001"
    assert payload["clients"][0]["name"] == "Alice Driver"
    assert payload["premium_products"][0]["name"] == "Alpha Auto Plus"
    assert "QA-1001" in summary
    assert "PA-1001" in summary
    assert "Alpha Auto Plus" in summary

    filter_text = "\n".join(str(criteria) for _, query in db.queries for criteria in query.filters)
    filter_values = [
        getattr(getattr(criteria, "right", None), "value", None)
        for _, query in db.queries
        for criteria in query.filters
    ]
    assert filter_values.count(company_id) >= 4
    assert "quotes.company_id" in filter_text
    assert "policies.company_id" in filter_text
    assert "client_company.company_id" in filter_text
    assert "premium_policy_types.company_id" in filter_text


def test_invalid_company_context_does_not_query_database():
    class NoQueryDatabase:
        def query(self, *args, **kwargs):
            raise AssertionError("database should not be queried without a valid company_id")

    payload = build_tenant_context_payload(NoQueryDatabase(), None)

    assert payload["tenant_scope"] == {"company_id": None, "is_scoped": False}
    assert payload["quotes"] == []
    assert payload["policies"] == []


def test_quote_agent_prompt_receives_tenant_context(monkeypatch):
    fake_genai = ModuleType("google.generativeai")
    fake_genai.configure = lambda *args, **kwargs: None
    fake_genai.GenerativeModel = lambda *args, **kwargs: SimpleNamespace(generate_content=lambda prompt: SimpleNamespace(text=""))
    monkeypatch.setitem(sys.modules, "google.generativeai", fake_genai)

    from agents.a2a_quote_agent import agent_executor as quote_module

    company_id = uuid4()
    user_id = uuid4()
    client_id = uuid4()
    captured = {}

    class FakeAgent:
        def __init__(self, *args, **kwargs):
            pass

        async def run(self, prompt, **kwargs):
            captured["prompt"] = prompt
            return "I can help with your quote."

    class FakeSession:
        def __init__(self):
            self.user = SimpleNamespace(id=user_id, role="client")
            self.client = SimpleNamespace(id=client_id, first_name="Grace", last_name="Driver")

        def query(self, model):
            if model is User:
                return QueryDouble([self.user])
            if model is Client:
                return QueryDouble([self.client])
            return QueryDouble([])

        def close(self):
            pass

    class FakeQueue:
        def __init__(self):
            self.events = []

        def enqueue_event(self, event):
            self.events.append(event)

    monkeypatch.setattr(quote_module, "Agent", FakeAgent)
    monkeypatch.setattr(quote_module, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(
        quote_module,
        "build_tenant_context_summary",
        lambda db, tenant_company_id: "[SYSTEM DATABASE CONTEXT - TENANT SCOPED] {\"quotes\":[{\"quote_number\":\"QG-3001\"}],\"premium_products\":[{\"name\":\"Gamma Auto\"}]}",
    )

    executor = quote_module.QuoteAgentExecutor()
    context = SimpleNamespace(
        metadata={
            "company_id": str(company_id),
            "user_id": str(user_id),
            "history": [{"role": "user", "text": "Show my recent quote"}],
        },
        events=[SimpleNamespace(type="user_text_message", text="Show my recent quote")],
    )
    queue = FakeQueue()

    asyncio.run(executor.execute(context, queue))

    assert "[SYSTEM DATABASE CONTEXT - TENANT SCOPED]" in captured["prompt"]
    assert "QG-3001" in captured["prompt"]
    assert "Gamma Auto" in captured["prompt"]
    assert str(company_id) in captured["prompt"]
    assert str(client_id) in captured["prompt"]
    assert queue.events
