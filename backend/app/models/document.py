"""
Document model for file management and collaboration.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Integer, Boolean
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Integer, Boolean
from sqlalchemy.orm import relationship
import uuid
from app.core.guid import GUID
from datetime import datetime
import enum

from app.core.database import Base

class DocumentLabel(str, enum.Enum):
    QUOTE = 'Quote'
    POLICY = 'Policy'
    RECEIPT = 'Receipt'
    PAYSLIP = 'Payslip'
    DOCUMENT = 'Document'
    ADS = 'Ads'
    DRIVING_LICENCE = 'Driving Licence'
    CAR_PAPERS = 'Car Papers'
    PHOTO = 'Photo'
    AGREEMENT = 'Agreement'

class Document(Base):
    """Model for storing document metadata."""
    __tablename__ = "documents"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_type = Column(String(50)) # pdf, jpg, etc.
    file_size = Column(Integer) # in bytes
    
    label = Column(Enum(DocumentLabel), default=DocumentLabel.DOCUMENT)
    
    # Visibility: If PUBLIC, acts as a dataset entry. If PRIVATE, relies on InterCompanyShare.
    # Visibility & Sharing Defaults
    visibility = Column(String(20), default='PRIVATE') # 'PUBLIC', 'PRIVATE'
    scope = Column(String(20), default='B2B') # 'B2B', 'B2C', etc.
    is_shareable = Column(Boolean, default=False)
    reshare_rule = Column(String(1), default='C') # 'A', 'B', 'C'
    
    uploaded_by = Column(GUID(), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="documents")
    uploader = relationship("User")
    shares = relationship("InterCompanyShare", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document {self.name} ({self.label})>"
