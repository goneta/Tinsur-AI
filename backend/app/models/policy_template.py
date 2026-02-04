"""
Policy Template model for customizable insurance policy templates.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.time import utcnow

from app.core.database import Base


class PolicyTemplate(Base):
    """Policy Template model for customizable policy templates."""
    __tablename__ = "policy_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    policy_type_id = Column(UUID(as_uuid=True), ForeignKey("policy_types.id", ondelete="CASCADE"))
    
    # Template identification
    name = Column(String(200), nullable=False)
    code = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Template content
    template_content = Column(JSON, default={})  # Rich template structure
    field_definitions = Column(JSON, default=[])  # Dynamic field configurations
    
    # Versioning
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    # Localization
    language = Column(String(10), default='fr')  # 'fr', 'en', etc.
    
    # Legal clauses
    terms_and_conditions = Column(Text)
    legal_clauses = Column(JSON, default=[])
    
    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    company = relationship("Company")
    policy_type = relationship("PolicyType")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<PolicyTemplate {self.name} v{self.version}>"
