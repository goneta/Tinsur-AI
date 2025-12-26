import sys
import os
from sqlalchemy import text

# Add parent directory to path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
# Import all models to ensure mappers are initialized
from app.models.company import Company
from app.models.user import User
from app.models.client import Client
from app.models.policy_type import PolicyType
from app.models.policy_service import PolicyService
from app.models.pos_location import POSLocation
from app.models.regulatory import IFRS17Group
from app.models.endorsement import Endorsement
from app.models.co_insurance import CoInsuranceShare
from app.models.quote import Quote
from app.models.policy import Policy
from app.models.claim import Claim
from app.models.premium_policy import PremiumPolicyType
from app.core.config import settings

def debug_services():
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    db = SessionLocal()
    try:
        print("Checking tables...")
        # Check if table exists
        result = db.execute(text("SELECT to_regclass('public.premium_policy_service_association')")).scalar()
        print(f"Table 'premium_policy_service_association' exists: {result}")

        # Get a policy type and a service
        policy_type = db.query(PremiumPolicyType).first()
        service = db.query(PolicyService).first()

        if not policy_type or not service:
            print("Missing data (PolicyType or Service)")
            return

        print(f"Policy Type: {policy_type.name} ({policy_type.id})")
        print(f"Service: {service.name_en} ({service.id})")

        # Try to associate
        print("Attempting to associate...")
        if service not in policy_type.services:
            policy_type.services.append(service)
            db.commit()
            print("Associated!")
        else:
            print("Already associated.")

        # Reload
        db.refresh(policy_type)
        print(f"Policy Services count: {len(policy_type.services)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_services()
