"""
Archive service for cryptographic hashing and document integrity verification.
"""
import hashlib
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional, Tuple
from datetime import datetime

from app.models.archive import PolicyArchive
from app.models.policy import Policy

class ArchiveService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_hash(self, file_content: bytes) -> str:
        """Calculate SHA-256 hash of file content."""
        return hashlib.sha256(file_content).hexdigest()

    def archive_policy_document(
        self, 
        policy_id: UUID, 
        document_url: str, 
        file_content: bytes
    ) -> PolicyArchive:
        """
        Create an immutable record of a policy document's hash.
        """
        policy = self.db.query(Policy).get(policy_id)
        if not policy:
            raise ValueError("Policy not found")
            
        document_hash = self.calculate_hash(file_content)
        
        # Get latest version for this policy
        latest_version = self.db.query(PolicyArchive).filter(
            PolicyArchive.policy_id == policy_id
        ).order_by(PolicyArchive.archive_version.desc()).first()
        
        new_version = (latest_version.archive_version + 1) if latest_version else 1
        
        archive = PolicyArchive(
            company_id=policy.company_id,
            policy_id=policy_id,
            document_hash=document_hash,
            document_url=document_url,
            archive_version=new_version
        )
        self.db.add(archive)
        self.db.commit()
        self.db.refresh(archive)
        return archive

    def verify_document_integrity(self, policy_id: UUID, file_content: bytes) -> Tuple[bool, Optional[PolicyArchive]]:
        """
        Check if the provided file content matches the archived hash for a policy.
        """
        document_hash = self.calculate_hash(file_content)
        
        # Check against any version of the archive for this policy
        archive = self.db.query(PolicyArchive).filter(
            PolicyArchive.policy_id == policy_id,
            PolicyArchive.document_hash == document_hash
        ).first()
        
        if archive:
            return True, archive
        return False, None

    def get_archives_for_policy(self, policy_id: UUID) -> List[PolicyArchive]:
        """Get history of document versions for a policy."""
        return self.db.query(PolicyArchive).filter(
            PolicyArchive.policy_id == policy_id
        ).order_by(PolicyArchive.archive_version.desc()).all()
