"""
Task model for internal workflow tracking.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
import uuid
from app.core.guid import GUID
from app.core.time import utcnow

from app.core.database import Base


class Task(Base):
    """Task model."""
    __tablename__ = "tasks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    assigned_to = Column(GUID(), ForeignKey("users.id"), nullable=True)
    created_by = Column(GUID(), ForeignKey("users.id"), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(String(50), default="medium")  # low, medium, high, urgent
    status = Column(String(50), default="pending")  # pending, in_progress, completed, cancelled
    due_date = Column(Date)

    related_resource = Column(String(100))  # e.g., "claim", "policy", "quote"
    related_resource_id = Column(GUID(), nullable=True)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company")
    assignee = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Task {self.title}>"
