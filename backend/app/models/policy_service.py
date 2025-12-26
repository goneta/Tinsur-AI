from sqlalchemy import Column, String, Boolean, ForeignKey, Table, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

# Association table for Policy <-> PolicyService
policy_service_association = Table(
    'policy_service_association',
    Base.metadata,
    Column('policy_id', UUID(as_uuid=True), ForeignKey('policies.id', ondelete="CASCADE"), primary_key=True),
    Column('service_id', UUID(as_uuid=True), ForeignKey('policy_services.id', ondelete="CASCADE"), primary_key=True),
    Column('price', Numeric(15, 2), nullable=False, default=0.00)  # Snapshot price at time of linkage
)

class PolicyService(Base):
    """Policy Service model (optional add-ons)."""
    __tablename__ = "policy_services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True)

    name_en = Column(String(255), nullable=False)
    name_fr = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    default_price = Column(Numeric(15, 2), default=0.00)
    is_active = Column(Boolean, default=True)

    # Relationships
    company = relationship("Company")
    # policies relationship will be defined on Policy model
    
    def __repr__(self):
        return f"<PolicyService {self.name_en}>"
