"""
Pydantic schemas for policy templates.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class FieldDefinition(BaseModel):
    """Schema for dynamic field definition."""
    field_name: str
    field_type: str  # 'text', 'number', 'date', 'select', 'checkbox', etc.
    label: str
    required: bool = False
    default_value: Optional[Any] = None
    options: Optional[List[str]] = None  # For select fields
    validation_rules: Optional[Dict[str, Any]] = None


class PolicyTemplateBase(BaseModel):
    """Base schema for policy template."""
    name: str = Field(..., max_length=200)
    code: str = Field(..., max_length=100)
    description: Optional[str] = None
    policy_type_id: UUID
    template_content: Optional[Dict[str, Any]] = None
    field_definitions: Optional[List[FieldDefinition]] = []
    language: str = Field(default='fr', max_length=10)
    terms_and_conditions: Optional[str] = None
    legal_clauses: Optional[List[Dict[str, Any]]] = []
    is_active: bool = True


class PolicyTemplateCreate(PolicyTemplateBase):
    """Schema for creating a policy template."""
    pass


class PolicyTemplateUpdate(BaseModel):
    """Schema for updating a policy template."""
    name: Optional[str] = Field(None, max_length=200)
    code: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    template_content: Optional[Dict[str, Any]] = None
    field_definitions: Optional[List[FieldDefinition]] = None
    language: Optional[str] = Field(None, max_length=10)
    terms_and_conditions: Optional[str] = None
    legal_clauses: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None


class PolicyTemplateResponse(PolicyTemplateBase):
    """Schema for policy template response."""
    id: UUID
    company_id: UUID
    version: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PolicyTemplateListResponse(BaseModel):
    """Schema for policy template list response."""
    templates: List[PolicyTemplateResponse]
    total: int
    page: int = 1
    page_size: int = 50
