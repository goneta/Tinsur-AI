"""
Focused tests for Milestone 7 automatic policy document packet orchestration.
"""
from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

from app.models.client import Client
from app.models.company import Company
from app.models.document import Document, DocumentLabel
from app.schemas.product_catalog import ProductPolicyAcquisitionRequest, ProductQuoteRequest
from app.services.product_policy_acquisition_service import ProductPolicyAcquisitionService
from app.services.product_policy_document_packet_service import ProductPolicyDocumentPacketService


class _FakeQuery:
    def __init__(self, db, model):
        self.db = db
        self.model = model

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def all(self):
        if self.model is Document:
            return list(self.db.documents)
        return []

    def first(self):
        if self.model is Client:
            return self.db.client
        if self.model is Company:
            return self.db.company
        return None


class _FakeDB:
    def __init__(self, documents=None, client=None, company=None):
        self.documents = list(documents or [])
        self.client = client or SimpleNamespace(id=uuid4(), display_name="Ava Client")
        self.company = company or SimpleNamespace(id=uuid4(), name="Tinsur Demo")

    def query(self, model):
        return _FakeQuery(self, model)


class _FakeGenerator:
    def __init__(self, db):
        self.db = db
        self.calls = 0

    def generate_documents(self, db, policy, client, company):
        self.calls += 1
        generated = Document(
            id=uuid4(),
            company_id=policy.company_id,
            policy_id=policy.id,
            client_id=policy.client_id,
            name=f"Policy_{policy.policy_number}.pdf",
            file_url=f"/documents/{policy.id}/policy.pdf",
            file_type="pdf",
            label=DocumentLabel.POLICY,
            verification_code="VERIFY77",
        )
        db.documents.append(generated)
        return [generated.file_url]


def _policy(company_id=None, client_id=None):
    return SimpleNamespace(
        id=uuid4(),
        company_id=company_id or uuid4(),
        client_id=client_id or uuid4(),
        policy_number="POL-M7-001",
        client=None,
        company=None,
    )


def _document(policy):
    return Document(
        id=uuid4(),
        company_id=policy.company_id,
        policy_id=policy.id,
        client_id=policy.client_id,
        name="Policy_POL-M7-001.pdf",
        file_url=f"/documents/{policy.id}/policy-existing.pdf",
        file_type="pdf",
        label=DocumentLabel.POLICY,
        verification_code="EXIST77",
    )


def _acquisition_request(**overrides):
    payload = {
        "client_id": uuid4(),
        "quote_request": ProductQuoteRequest(
            product_code="CAR_STANDARD",
            applicant_data={"first_name": "Ava", "last_name": "Client"},
            risk_data={"vehicle": {"market_value": 20000}, "driver": {"age": 35}},
        ),
        "auto_issue_policy": True,
    }
    payload.update(overrides)
    return ProductPolicyAcquisitionRequest(**payload)


def test_milestone7_acquisition_request_defaults_to_document_generation():
    request = _acquisition_request()

    assert request.generate_policy_documents is True
    assert request.regenerate_policy_documents is False


def test_milestone7_document_packet_returns_existing_documents_idempotently():
    policy = _policy()
    existing = _document(policy)
    db = _FakeDB(documents=[existing])
    generator = _FakeGenerator(db)
    service = ProductPolicyDocumentPacketService(db, generator=generator)

    packet = service.generate_packet(policy.company_id, policy)

    assert packet["status"] == "existing"
    assert packet["generated_count"] == 0
    assert generator.calls == 0
    assert packet["documents"] == [
        {
            "document_id": existing.id,
            "name": "Policy_POL-M7-001.pdf",
            "file_url": existing.file_url,
            "file_type": "pdf",
            "verification_code": "EXIST77",
        }
    ]


def test_milestone7_document_packet_generates_missing_policy_documents():
    policy = _policy()
    db = _FakeDB()
    generator = _FakeGenerator(db)
    service = ProductPolicyDocumentPacketService(db, generator=generator)

    packet = service.generate_packet(policy.company_id, policy)

    assert packet["status"] == "generated"
    assert packet["generated_count"] == 1
    assert generator.calls == 1
    assert packet["documents"][0]["file_url"].endswith("/policy.pdf")
    assert packet["documents"][0]["verification_code"] == "VERIFY77"


def test_milestone7_document_packet_rejects_cross_tenant_policy():
    policy = _policy()
    db = _FakeDB()
    service = ProductPolicyDocumentPacketService(db, generator=_FakeGenerator(db))

    try:
        service.generate_packet(uuid4(), policy)
    except ValueError as exc:
        assert "tenant" in str(exc)
    else:
        raise AssertionError("Expected cross-tenant document packet generation to fail")


def test_milestone7_acquisition_response_includes_document_packet_metadata():
    quote = SimpleNamespace(id=uuid4(), quote_number="CAR-123", status="policy_created")
    policy = SimpleNamespace(id=uuid4(), policy_number="POL-123", status="active")
    document_id = uuid4()

    response = ProductPolicyAcquisitionService._build_response(
        quote,
        {
            "decision": "approved",
            "product_id": uuid4(),
            "product_code": "CAR_STANDARD",
            "product_name": "Car Standard",
            "product_line": "car",
            "product_version_id": uuid4(),
            "product_version": "2026.1",
            "currency": "USD",
            "term_months": 12,
            "rating_base": "20000.00",
            "base_premium": "1000.00",
            "subtotal_premium": "1200.00",
            "taxes_and_fees_total": "120.00",
            "estimated_premium": "1320.00",
            "is_eligible": True,
            "referral_required": False,
            "decision_reasons": [],
            "coverage_breakdown": [],
            "factor_breakdown": [],
            "underwriting_decisions": [],
            "taxes_and_fees": [],
            "wizard_schema": None,
        },
        policy,
        idempotent=False,
        document_packet={
            "status": "generated",
            "documents": [
                {
                    "document_id": document_id,
                    "name": "Policy_POL-123.pdf",
                    "file_url": "/documents/policy.pdf",
                    "file_type": "pdf",
                    "verification_code": "DOC777",
                }
            ],
        },
    )

    assert response["status"] == "policy_issued"
    assert response["document_status"] == "generated"
    assert response["documents"][0]["document_id"] == document_id
    assert response["documents"][0]["verification_code"] == "DOC777"


def test_milestone7_acquisition_can_skip_document_generation_until_policy_exists():
    service = ProductPolicyAcquisitionService(_FakeDB())

    assert service._document_packet(uuid4(), None, _acquisition_request())["status"] == "not_available"
    assert service._document_packet(uuid4(), _policy(), _acquisition_request(generate_policy_documents=False))["status"] == "not_requested"
