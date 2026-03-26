"""Help and Onboarding Guide Models"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.models import Base


class GuideType(str, enum.Enum):
    """Types of guides available"""
    CLIENT = "client"
    ADMIN = "admin"
    INSURANCE_COMPANY = "insurance_company"


class GuideSection(str, enum.Enum):
    """Guide sections for context-sensitive help"""
    GETTING_STARTED = "getting_started"
    CLIENT_MANAGEMENT = "client_management"
    QUOTE_CREATION = "quote_creation"
    POLICY_MANAGEMENT = "policy_management"
    REPORTS = "reports"
    USER_MANAGEMENT = "user_management"
    SECURITY = "security"
    INTEGRATIONS = "integrations"
    TROUBLESHOOTING = "troubleshooting"


class HelpGuide(Base):
    """Help guide model for storing onboarding content"""
    __tablename__ = "help_guides"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    content = Column(Text)  # Markdown content
    guide_type = Column(Enum(GuideType), index=True)
    section = Column(Enum(GuideSection), index=True, nullable=True)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    tags = Column(String, nullable=True)  # Comma-separated tags for search
    estimated_read_time = Column(Integer, default=5)  # Minutes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    completions = relationship("GuideCompletion", back_populates="guide", cascade="all, delete-orphan")
    accesses = relationship("GuideAccess", back_populates="guide", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<HelpGuide {self.id}>"


class GuideCompletion(Base):
    """Track which guides users have completed"""
    __tablename__ = "guide_completions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id"), index=True)
    guide_id = Column(String, ForeignKey("help_guides.id"), index=True)
    completed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    guide = relationship("HelpGuide", back_populates="completions")

    def __repr__(self):
        return f"<GuideCompletion user={self.user_id} guide={self.guide_id}>"


class GuideAccess(Base):
    """Track guide access for analytics"""
    __tablename__ = "guide_accesses"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id"), index=True, nullable=True)
    guide_id = Column(String, ForeignKey("help_guides.id"), index=True)
    section_accessed = Column(String, nullable=True)  # Specific section within guide
    accessed_at = Column(DateTime, default=datetime.utcnow, index=True)
    time_spent_seconds = Column(Integer, default=0)  # How long they viewed it
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    guide = relationship("HelpGuide", back_populates="accesses")

    def __repr__(self):
        return f"<GuideAccess guide={self.guide_id} at={self.accessed_at}>"


class OnboardingStatus(Base):
    """Track user onboarding progress"""
    __tablename__ = "onboarding_status"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id"), unique=True, index=True)
    current_step = Column(Integer, default=0)  # Current step in onboarding wizard
    completed = Column(Boolean, default=False)
    skipped = Column(Boolean, default=False)
    last_accessed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<OnboardingStatus user={self.user_id} completed={self.completed}>"
