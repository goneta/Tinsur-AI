
import sys
import os
import logging

# Add parent directory to path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_admin_password():
    db = SessionLocal()
    try:
        email = "admin@demoinsurance.com"
        new_password = "admin123"
        
        logger.info(f"Updating password for {email}...")
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.error(f"User {email} not found!")
            return
            
        hashed_password = get_password_hash(new_password)
        user.password_hash = hashed_password
        db.commit()
        
        logger.info(f"Successfully updated password for {email} to '{new_password}'")
        
    except Exception as e:
        logger.error(f"Error updating password: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin_password()
