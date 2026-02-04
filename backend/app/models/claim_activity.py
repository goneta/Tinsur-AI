"""
Claim activity log model.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import uuid
from app.core.guid import GUID
from app.core.time import utcnow

from app.core.database import Base


class ClaimActivity(Base):
    """Activity log for claim actions."""
    __tablename__ = "claim_activities"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    claim_id = Column(GUID(), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=utcnow)

    claim = relationship("Claim", back_populates="activities")
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<ClaimActivity {self.action}>"
