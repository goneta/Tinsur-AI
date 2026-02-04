"""
OCR service for document processing.
"""
from typing import Dict, Any, Optional
from uuid import uuid4
import re
import asyncio

from app.core.database import get_mongodb
from app.core.time import utcnow
from app.services.ai_service import AiService


class OCRService:
    """Service to extract text/fields from documents."""

    def __init__(self, db):
        self.db = db
        self.ai_service = AiService(db)
        self.mongo = get_mongodb()

    def _classify_document(self, text: str) -> str:
        """Simple heuristic-based document classification."""
        text_lower = text.lower()
        if "driver" in text_lower or "license" in text_lower:
            return "driver_license"
        if "passport" in text_lower:
            return "passport"
        if "vehicle" in text_lower or "registration" in text_lower or "vin" in text_lower:
            return "vehicle_registration"
        if "policy" in text_lower or "insurance" in text_lower:
            return "insurance_document"
        return "unknown"

    async def _extract_text_with_ai(self, image_bytes: bytes, company_id: Optional[str]) -> str:
        """Use Gemini to extract raw text from an image."""
        api_key, _, has_credits = self.ai_service.get_effective_ai_config(company_id)
        if not api_key or not has_credits:
            return ""

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3-flash-preview')
            prompt = "Extract all visible text from this document. Return plain text only."
            response = await asyncio.to_thread(
                model.generate_content,
                [prompt, {"mime_type": "image/jpeg", "data": image_bytes}],
            )
            return getattr(response, "text", "") or ""
        except Exception:
            return ""

    async def process_document(self, image_bytes: bytes, company_id: Optional[str], document_type: Optional[str] = None) -> Dict[str, Any]:
        """Process a document and store extraction in MongoDB."""
        extracted_fields: Dict[str, Any] = {}
        confidence_scores: Dict[str, Any] = {}
        extraction_method = "ocr"

        # If document type is known and supported by KYC parser, use it
        if document_type in ["identity_document", "car_papers"]:
            extracted_fields = await self.ai_service.parse_kyc_document_bytes(
                image_bytes,
                doc_type=document_type,
                company_id=company_id,
            )
            confidence_scores = {"overall": 0.8}
        else:
            # Use AI to extract raw text and try to classify
            raw_text = await self._extract_text_with_ai(image_bytes, company_id)
            document_type = document_type or self._classify_document(raw_text)
            extracted_fields = {
                "raw_text": raw_text,
            }
            # Attempt to parse basic fields from text
            if raw_text:
                name_match = re.search(r"name[:\s]+([A-Za-z\\s]+)", raw_text, re.IGNORECASE)
                if name_match:
                    extracted_fields["name"] = name_match.group(1).strip()
            confidence_scores = {"overall": 0.6 if raw_text else 0.0}

        document_id = str(uuid4())
        record = {
            "document_id": document_id,
            "document_type": document_type or "unknown",
            "extraction_method": extraction_method,
            "confidence_scores": confidence_scores,
            "extracted_fields": extracted_fields,
            "validation_status": "pending",
            "verified_by": None,
            "verified_at": None,
            "created_at": utcnow(),
        }

        self.mongo.extracted_documents.insert_one(record)
        return record

    def get_result(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Fetch OCR result by document_id."""
        result = self.mongo.extracted_documents.find_one({"document_id": document_id})
        if not result:
            return None
        result.pop("_id", None)
        return result

    def verify_result(self, document_id: str, status: str, verified_by: Optional[str], notes: Optional[str]) -> Optional[Dict[str, Any]]:
        """Verify extracted data."""
        update = {
            "validation_status": status,
            "verified_by": verified_by,
            "verified_at": utcnow(),
        }
        if notes:
            update["verification_notes"] = notes

        self.mongo.extracted_documents.update_one(
            {"document_id": document_id},
            {"$set": update},
        )
        return self.get_result(document_id)
