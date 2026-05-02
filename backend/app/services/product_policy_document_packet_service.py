"""
Milestone 7 policy document packet orchestration.

This service turns an issued policy into a tenant-scoped document/certificate
packet by reusing the existing template-backed DocumentService. It is designed
for post-acquisition flows where an approved product-catalog quote may issue a
policy and should immediately expose policy certificate metadata without forcing
the caller to invoke a separate documents endpoint.
"""
from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.company import Company
from app.models.document import Document, DocumentLabel
from app.models.policy import Policy
from app.services.document_service import document_service


class ProductPolicyDocumentPacketService:
    """Generate and list tenant-scoped policy document packets idempotently."""

    def __init__(self, db: Session, generator: Any = document_service):
        self.db = db
        self.generator = generator

    def generate_packet(
        self,
        company_id: UUID,
        policy: Policy,
        regenerate: bool = False,
    ) -> dict[str, Any]:
        """Generate missing policy documents or return the existing packet."""
        self._validate_policy_scope(company_id, policy)

        existing_documents = self._policy_documents(company_id, policy.id)
        if existing_documents and not regenerate:
            return {
                "status": "existing",
                "generated_count": 0,
                "documents": [self._document_item(document) for document in existing_documents],
            }

        client = self._resolve_client(policy)
        company = self._resolve_company(company_id, policy)
        if not client or not company:
            raise ValueError("Policy document generation requires a tenant-scoped client and company")

        generated_urls = self.generator.generate_documents(self.db, policy, client, company) or []
        documents = self._policy_documents(company_id, policy.id)
        return {
            "status": "generated" if generated_urls else "no_templates",
            "generated_count": len(generated_urls),
            "documents": [self._document_item(document) for document in documents],
        }

    def list_packet(self, company_id: UUID, policy_id: UUID) -> dict[str, Any]:
        """Return the current tenant-scoped policy document packet without side effects."""
        documents = self._policy_documents(company_id, policy_id)
        return {
            "status": "existing" if documents else "not_generated",
            "generated_count": 0,
            "documents": [self._document_item(document) for document in documents],
        }

    @staticmethod
    def _validate_policy_scope(company_id: UUID, policy: Optional[Policy]) -> None:
        if not policy or policy.company_id != company_id:
            raise ValueError("Policy not found for this tenant")

    def _policy_documents(self, company_id: UUID, policy_id: UUID) -> list[Document]:
        return (
            self.db.query(Document)
            .filter(
                Document.company_id == company_id,
                Document.policy_id == policy_id,
                Document.label == DocumentLabel.POLICY,
            )
            .order_by(Document.created_at.asc())
            .all()
        )

    def _resolve_client(self, policy: Policy) -> Optional[Client]:
        if getattr(policy, "client", None):
            return policy.client
        return self.db.query(Client).filter(Client.id == policy.client_id).first()

    def _resolve_company(self, company_id: UUID, policy: Policy) -> Optional[Company]:
        if getattr(policy, "company", None):
            return policy.company
        return self.db.query(Company).filter(Company.id == company_id).first()

    @staticmethod
    def _document_item(document: Document) -> dict[str, Any]:
        return {
            "document_id": document.id,
            "name": document.name,
            "file_url": document.file_url,
            "file_type": document.file_type,
            "verification_code": document.verification_code,
        }
