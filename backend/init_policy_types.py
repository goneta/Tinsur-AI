#!/usr/bin/env python
"""
Initialize default policy types for companies.
Run this once to set up standard insurance policy types.
"""

from sqlalchemy.orm import Session
import uuid
from app.core.database import SessionLocal
from app.models.policy_type import PolicyType
from app.models.company import Company

def init_policy_types():
    """Create default policy types for all companies."""
    db = SessionLocal()
    
    try:
        # Get all companies
        companies = db.query(Company).all()
        
        if not companies:
            print("[INFO] No companies found. Please create a company first.")
            return
        
        # Standard policy types
        policy_types = [
            {"code": "AUTO", "name": "Auto/Vehicle Insurance", "description": "Vehicle and automobile insurance coverage"},
            {"code": "HOME", "name": "Home/Property Insurance", "description": "Home and property insurance coverage"},
            {"code": "HEALTH", "name": "Health Insurance", "description": "Health and medical insurance coverage"},
            {"code": "LIFE", "name": "Life Insurance", "description": "Life insurance coverage"},
            {"code": "TRAVEL", "name": "Travel Insurance", "description": "Travel and trip insurance coverage"},
            {"code": "BUSINESS", "name": "Business Insurance", "description": "Business and liability insurance coverage"},
        ]
        
        for company in companies:
            print(f"\nProcessing company: {company.name}")
            
            for policy_type_data in policy_types:
                # Check if this policy type already exists for this company
                existing = db.query(PolicyType).filter(
                    PolicyType.company_id == company.id,
                    PolicyType.code == policy_type_data["code"]
                ).first()
                
                if existing:
                    print(f"  [OK] {policy_type_data['name']} already exists")
                else:
                    # Create new policy type
                    policy_type = PolicyType(
                        id=uuid.uuid4(),
                        company_id=company.id,
                        code=policy_type_data["code"],
                        name=policy_type_data["name"],
                        description=policy_type_data["description"],
                        is_active=True
                    )
                    db.add(policy_type)
                    print(f"  [OK] Created {policy_type_data['name']}")
        
        # Commit all changes
        db.commit()
        print("\n[SUCCESS] Policy types initialized successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error initializing policy types: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    init_policy_types()
