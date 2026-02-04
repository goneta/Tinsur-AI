"""
OCR schemas.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class OCRProcessRequest(BaseModel):
    document_url: Optional[str] = None
    document_type: Optional[str] = None


class OCRProcessResponse(BaseModel):
    document_id: str
    document_type: str
    extraction_method: str
    extracted_fields: Dict[str, Any]
    confidence_scores: Dict[str, Any]
    validation_status: str
    created_at: datetime


class OCRVerifyRequest(BaseModel):
    document_id: str = Field(..., min_length=1)
    status: str = Field(..., pattern="^(verified|rejected)$")
    verified_by: Optional[str] = None
    notes: Optional[str] = None

