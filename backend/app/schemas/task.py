"""
Task schemas.
"""
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    status: str = Field(default="pending", pattern="^(pending|in_progress|completed|cancelled)$")
    due_date: Optional[date] = None
    related_resource: Optional[str] = None
    related_resource_id: Optional[UUID] = None
    assigned_to: Optional[UUID] = None


class TaskCreate(TaskBase):
    company_id: Optional[UUID] = None
    created_by: Optional[UUID] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = Field(default=None, pattern="^(low|medium|high|urgent)$")
    status: Optional[str] = Field(default=None, pattern="^(pending|in_progress|completed|cancelled)$")
    due_date: Optional[date] = None
    related_resource: Optional[str] = None
    related_resource_id: Optional[UUID] = None
    assigned_to: Optional[UUID] = None


class TaskResponse(TaskBase):
    id: UUID
    company_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
