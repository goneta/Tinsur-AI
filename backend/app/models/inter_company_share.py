"""
Inter-Company Share model for secure collaboration.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.guid import GUID
from app.core.database import Base
# Client and User imports are usually handled by string reference in relationships to avoid circular imports, 

class InterCompanyShare(Base):
    """Model for tracking shared resources between companies."""
    __tablename__ = "inter_company_shares"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    from_company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Target Entities (Polymorphic-style)
    to_company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True)
    to_client_id = Column(GUID(), ForeignKey("clients.id", ondelete="CASCADE"), nullable=True)
    to_user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    
    resource_type = Column(String(50), nullable=False) # 'document', etc.
    resource_id = Column(GUID(), nullable=False)
    
    # Financial fields for settlements
    amount = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default='XOF')
    
    # Document specific relationship (if resource_type == 'document')
    # logic handled by app, but nice to have foreign key if possible. 
    # Since resource_id can be polymorphic, we might not set FK here strictly or use a specialized approach.
    # For now, we manually join or use property.
    # To enable back_populates from Document, we need a FK specifically for doc or a polymorphic join.
    # Simpler approach: Add `document_id` nullable for now to support direct relation.
    document_id = Column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True)
    document = relationship("Document", back_populates="shares")

    # Scope and Permissions
    # B2B, B2C, B2E, E2E, C2C
    scope = Column(String(10), default='B2B') 
    
    # Sharing Option: 1 (Not Shareable), 2 (Shareable)
    is_reshareable = Column(Boolean, default=False)
    
    # Reshare Rule: A (Extended), B (Once), C (None - redundant if is_reshareable is False, but useful logic)
    reshare_rule = Column(String(1), nullable=True) # 'A', 'B', 'C'
    
    access_level = Column(String(50), default='read') # 'read', 'write'
    expires_at = Column(DateTime, nullable=True)
    is_revoked = Column(Boolean, default=False)
    notes = Column(String(500), nullable=True) # Description or memo
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    from_company = relationship("Company", foreign_keys=[from_company_id])
    to_company = relationship("Company", foreign_keys=[to_company_id])
    to_client = relationship("Client", foreign_keys=[to_client_id])
    to_user = relationship("User", foreign_keys=[to_user_id])
    
    def __repr__(self):
        return f"<InterCompanyShare {self.id} {self.resource_type} {self.scope}>"
