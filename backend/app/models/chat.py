"""
Internal chat models for staff communication.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Text, UniqueConstraint
from sqlalchemy.orm import relationship
import uuid
from app.core.guid import GUID
from app.core.time import utcnow

from app.core.database import Base


class ChatChannel(Base):
    """Chat channel for internal communication."""
    __tablename__ = "chat_channels"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    is_private = Column(Boolean, default=False)
    created_by = Column(GUID(), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=utcnow)

    company = relationship("Company")
    creator = relationship("User", foreign_keys=[created_by])
    messages = relationship("ChatMessage", back_populates="channel", cascade="all, delete-orphan")
    members = relationship("ChatChannelMember", back_populates="channel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatChannel {self.name}>"


class ChatMessage(Base):
    """Chat message."""
    __tablename__ = "chat_messages"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    channel_id = Column(GUID(), ForeignKey("chat_channels.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    message = Column(Text, nullable=False)
    attachments = Column(JSON, default=list)
    read_by = Column(JSON, default=list)
    reactions = Column(JSON, default=list)
    created_at = Column(DateTime, default=utcnow)

    channel = relationship("ChatChannel", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])

    def __repr__(self):
        return f"<ChatMessage {self.id}>"


class ChatChannelMember(Base):
    """Membership for private chat channels."""
    __tablename__ = "chat_channel_members"
    __table_args__ = (UniqueConstraint("channel_id", "user_id", name="uq_chat_channel_member"),)

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    channel_id = Column(GUID(), ForeignKey("chat_channels.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    added_by = Column(GUID(), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utcnow)

    channel = relationship("ChatChannel", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<ChatChannelMember {self.channel_id}:{self.user_id}>"
