import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal
from app.models.user import User
# Import all models to ensure mappers are initialized
from app.models.company import Company
from app.models.client import Client
from app.models.policy_type import PolicyType
from app.models.quote import Quote
from app.models.premium_policy import PremiumPolicyType
from app.models.policy_service import PolicyService
from app.models.regulatory import IFRS17Group
from app.models.pos_location import POSLocation
from app.models.endorsement import Endorsement
from app.models.claim import Claim
from app.models.co_insurance import CoInsuranceShare

def fix_admin_role():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@demoinsurance.com").first()
        if user:
            print(f"Current role: {user.role}")
            user.role = "company_admin"
            db.commit()
            print("Role updated to 'company_admin'")
        else:
            print("User not found!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin_role()
