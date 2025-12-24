"""
RBAC models: Role, Permission, RolePermission.
"""
from sqlalchemy import Column, String, ForeignKey, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

# Association table for Role <-> Permission (Many-to-Many)
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
)

class Permission(Base):
    """
    Granular permission definition.
    e.g. scope='policy', action='read' -> 'policy:read'
    """
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scope = Column(String(50), nullable=False) # e.g. "policy", "claim"
    action = Column(String(50), nullable=False) # e.g. "read", "write", "create"
    description = Column(String(255))
    
    # helper to get full string representation
    @property
    def key(self):
        return f"{self.scope}:{self.action}"

class Role(Base):
    """
    User Role definition.
    Overwrites/Enhances the string-based 'role' column in User table eventually, 
    or User table 'role' column references this, or we rely on string matching.
    For this implementation, we map string names to this table.
    """
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False) # e.g. "admin", "client"
    description = Column(Text)

    permissions = relationship("Permission", secondary="role_permissions", backref="roles")
