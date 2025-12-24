"""
Repository for policy template operations.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.policy_template import PolicyTemplate


class PolicyTemplateRepository:
    """Repository for policy template data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, template: PolicyTemplate) -> PolicyTemplate:
        """Create a new policy template."""
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template
    
    def get_by_id(self, template_id: UUID) -> Optional[PolicyTemplate]:
        """Get policy template by ID."""
        return self.db.query(PolicyTemplate).filter(PolicyTemplate.id == template_id).first()
    
    def get_by_company(
        self, 
        company_id: UUID, 
        policy_type_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        language: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[PolicyTemplate], int]:
        """Get policy templates by company with filters."""
        query = self.db.query(PolicyTemplate).filter(PolicyTemplate.company_id == company_id)
        
        if policy_type_id:
            query = query.filter(PolicyTemplate.policy_type_id == policy_type_id)
        if is_active is not None:
            query = query.filter(PolicyTemplate.is_active == is_active)
        if language:
            query = query.filter(PolicyTemplate.language == language)
        
        total = query.count()
        templates = query.order_by(PolicyTemplate.created_at.desc()).offset(skip).limit(limit).all()
        
        return templates, total
    
    def get_active_templates(self, company_id: UUID, policy_type_id: UUID) -> List[PolicyTemplate]:
        """Get active templates for a policy type."""
        return self.db.query(PolicyTemplate).filter(
            and_(
                PolicyTemplate.company_id == company_id,
                PolicyTemplate.policy_type_id == policy_type_id,
                PolicyTemplate.is_active == True
            )
        ).all()
    
    def update(self, template: PolicyTemplate) -> PolicyTemplate:
        """Update a policy template."""
        self.db.commit()
        self.db.refresh(template)
        return template
    
    def delete(self, template_id: UUID) -> bool:
        """Delete a policy template."""
        template = self.get_by_id(template_id)
        if template:
            self.db.delete(template)
            self.db.commit()
            return True
        return False
    
    def get_latest_version(self, company_id: UUID, code: str) -> Optional[PolicyTemplate]:
        """Get the latest version of a template by code."""
        return self.db.query(PolicyTemplate).filter(
            and_(
                PolicyTemplate.company_id == company_id,
                PolicyTemplate.code == code
            )
        ).order_by(PolicyTemplate.version.desc()).first()
