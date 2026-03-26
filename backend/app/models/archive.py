"""
Archive models for policy document integrity.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.time import utcnow

from app.core.database import Base

class PolicyArchive(Base):
    """
    Stores cryptographic hashes of policy documents to ensure legal proof of integrity.
    """
    __tablename__ = "policy_archives"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    
    # Cryptographic Fingerprint
    document_hash = Column(String(64), nullable=False, index=True) # SHA-256 hash (64 hex chars)
    hash_algorithm = Column(String(20), default="SHA-256")
    
    # Metadata
    document_url = Column(String(500)) # Link to the file at the time of archiving
    archive_version = Column(Integer, default=1) # Increment for endorsements/renewals
    
    archived_at = Column(DateTime, default=utcnow)
    
    # Relationships
    company = relationship("Company")
    policy = relationship("Policy")
