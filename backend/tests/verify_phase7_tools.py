
import sys
import os
import uuid
import logging
from datetime import datetime, date

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal, engine, Base
from app.models.company import Company
from app.models.client import Client
from app.models.policy import Policy
from app.models.loyalty import LoyaltyPoint
from app.models.referral import Referral
from app.models.ticket import Ticket
from app.models.telematics import TelematicsData
from app.models.ml_model import MLModel

# Import Tools
from agents.a2a_loyalty_agent.tools import get_loyalty_points, redeem_loyalty_points
from agents.a2a_referrals_agent.tools import get_referral_info, create_referral_link
from agents.a2a_tickets_agent.tools import create_support_ticket, get_ticket_status, list_active_tickets
from agents.a2a_telematics_agent.tools import get_driving_stats, get_safety_recommendations
from agents.a2a_ml_agent.tools import list_active_models, get_model_insight

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_phase7_tools():
    db = SessionLocal()
    try:
        logger.info("Setting up test data...")
        
        # Create Test Company
        company_id = uuid.uuid4()
        # Company: name, subdomain, email are required (non-nullable)
        # Assuming is_active=True by default. status column does not exist.
        company = Company(
            id=company_id, 
            name="Test Company Phase 7", 
            subdomain=f"test-p7-{uuid.uuid4().hex[:6]}", 
            email="contact@testp7.com"
        )
        db.merge(company)
        
        # Create Test Client
        client_id = uuid.uuid4()
        # Client: client_type required.
        client = Client(
            id=client_id, 
            company_id=company_id, 
            first_name="Test", 
            last_name="User", 
            email=f"test{uuid.uuid4()}@example.com",
            client_type="individual"
        )
        db.merge(client)
        
        # Create Test Policy
        policy_id = uuid.uuid4()
        # Policy: premium_amount, start_date, end_date required. type column does not exist.
        policy = Policy(
            id=policy_id, 
            company_id=company_id, 
            client_id=client_id, 
            policy_number=f"POL-{uuid.uuid4().hex[:8]}", 
            status="active", 
            start_date=date.today(), 
            end_date=date.today(),
            premium_amount=1000.00
            # policy_type_id is nullable (default) so we skip it to avoid creating dependency
        )
        db.merge(policy)
        
        # Setup Loyalty
        loyalty = LoyaltyPoint(client_id=client_id, points_balance=500, points_earned=500, tier="gold")
        db.add(loyalty)
        
        # Setup ML Model
        ml_model = MLModel(model_name="FraudDetector_v1", model_type="fraud_detection", model_version="1.0.0", accuracy=0.95, is_active=True, deployed_at=datetime.now())
        db.add(ml_model)

        # Setup Telematics
        telematics = TelematicsData(policy_id=policy_id, device_id="DEV-001", trip_date=date.today(), distance_km=100.0, avg_speed=60.0, max_speed=90.0, safety_score=95.0, harsh_braking_count=1)
        db.add(telematics)
        
        db.commit()
        
        logger.info("--- Testing Loyalty Tools ---")
        pts_info = get_loyalty_points(str(client_id))
        print(f"Points Info: {pts_info}")
        if "500 points" not in pts_info: raise Exception("Loyalty check failed")
        
        redeem_msg = redeem_loyalty_points(str(client_id), 100)
        print(f"Redeem: {redeem_msg}")
        if "Successfully redeemed" not in redeem_msg: raise Exception("Redemption failed")
        
        logger.info("--- Testing Referrals Tools ---")
        ref_link_msg = create_referral_link(str(client_id), str(company_id))
        print(f"Create Link: {ref_link_msg}")
        if "Created new referral link" not in ref_link_msg: raise Exception("Create referral link failed")
        
        ref_info = get_referral_info(str(client_id))
        print(f"Referral Info: {ref_info}")
        if "Active Codes" not in ref_info: raise Exception("Get referral info failed")

        logger.info("--- Testing Tickets Tools ---")
        ticket_msg = create_support_ticket(str(client_id), str(company_id), "Test Issue", "This is a test ticket")
        print(f"Create Ticket: {ticket_msg}")
        if "Ticket created successfully" not in ticket_msg: raise Exception("Create ticket failed")
        
        list_tickets = list_active_tickets(str(client_id))
        print(f"List Tickets: {list_tickets}")
        if "Test Issue" not in list_tickets: raise Exception("List tickets failed")
        
        # Extract ticket number for status check
        import re
        match = re.search(r"TKT-[A-Z0-9]+", ticket_msg)
        if match:
            tkt_num = match.group(0)
            status = get_ticket_status(tkt_num)
            print(f"Ticket Status: {status}")
            if "open" not in status: raise Exception("Get ticket status failed")
        else:
            print("Could not extract ticket number to test status")

        logger.info("--- Testing Telematics Tools ---")
        stats = get_driving_stats(str(policy_id))
        print(f"Driving Stats: {stats}")
        # Telematics tool returns formatted score e.g. 95.00/100
        if "95.0" not in stats: raise Exception(f"Get driving stats failed. Got: {stats}")
        
        recs = get_safety_recommendations(str(policy_id))
        print(f"Recs: {recs}")
        # "Great job" might depend on score threshold, 95.00 is > 90
        if "Great job" not in recs: raise Exception(f"Safety recommendations failed. Got: {recs}")

        logger.info("--- Testing ML Tools ---")
        active_models = list_active_models()
        print(f"Active Models: {active_models}")
        if "FraudDetector_v1" not in active_models: raise Exception("List active models failed")
        
        insight = get_model_insight("FraudDetector_v1")
        print(f"Insight: {insight}")
        # Tool formats as percentage: float(0.95)*100 -> 95.00%
        if "95.00%" not in insight: raise Exception(f"Model insight failed. Got: {insight}")

        logger.info("ALL TESTS PASSED SUCCESSFULLY")

    except Exception as e:
        logger.error(f"Verification Failed: {e}")
        import traceback
        traceback.print_exc()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    verify_phase7_tools()
