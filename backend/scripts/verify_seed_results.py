
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.models.company import Company
from app.models.premium_policy import PremiumPolicyType, PremiumPolicyCriteria
from app.models.policy_service import PolicyService
from app.models.quote import Quote
from app.models.regulatory import IFRS17Group
from app.models.pos_location import POSLocation
from app.models.endorsement import Endorsement
from app.models.claim import Claim
from app.models.co_insurance import CoInsuranceShare

def verify_data():
    db = SessionLocal()
    try:
        print(f"Companies: {db.query(Company).count()}")
        print(f"Services: {db.query(PolicyService).count()}")
        print(f"Premium Policies: {db.query(PremiumPolicyType).count()}")
        print(f"Criteria: {db.query(PremiumPolicyCriteria).count()}")
        print(f"Quotes: {db.query(Quote).count()}")
        
        # Check specific linkage
        pp = db.query(PremiumPolicyType).first()
        if pp:
            print(f"First Premium Policy: {pp.name}")
            print(f"  Services: {len(pp.services)}")
            print(f"  Criteria: {len(pp.criteria)}")
            
    finally:
        db.close()

if __name__ == "__main__":
    verify_data()
