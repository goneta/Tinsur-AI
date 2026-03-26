"""
Document template model for insurance document generation.
"""
from sqlalchemy import Column, String, DateTime, Text, JSON
import uuid
from app.core.guid import GUID
from app.core.time import utcnow

from app.core.database import Base


class DocumentTemplate(Base):
    """HTML template stored in DB for policy document generation."""
    __tablename__ = "document_templates"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    code = Column(String(150), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    language = Column(String(10), default="fr")
    template_html = Column(Text, nullable=False)
    placeholders = Column(JSON, default=list)
    source_path = Column(String(500))
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    def __repr__(self):
        return f"<DocumentTemplate {self.code}>"
