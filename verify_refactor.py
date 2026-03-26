
import sys
import os
import uuid
# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal
from app.models.client import Client
from app.models.company import Company
from backend.agents.a2a_referrals_agent.tools import get_referral_info, create_referral_link
from backend.agents.a2a_loyalty_agent.tools import get_loyalty_points, redeem_loyalty_points

def verify_refactor():
    db = SessionLocal()
    try:
        # Get a test client and company
        client = db.query(Client).first()
        if not client:
            print("No clients found. Cannot verify.")
            return

        company_id = str(client.company_id)
        client_id = str(client.id)

        print(f"Testing with Client: {client.first_name} {client.last_name} ({client_id})")
        print(f"Company ID: {company_id}")

        print("\n--- Testing Referral Agent Tools ---")
        # 1. Get Info (might be empty)
        info = get_referral_info(company_id, client_id)
        print(f"Referral Info (Pre-Creation):\n{info}")

        # 2. Create Link
        link_msg = create_referral_link(company_id, client_id)
        print(f"Create Link Result: {link_msg}")

        # 3. Get Info again (should have code)
        info_after = get_referral_info(company_id, client_id)
        print(f"Referral Info (Post-Creation):\n{info_after}")

        print("\n--- Testing Loyalty Agent Tools ---")
        # 1. Get Points
        points_msg = get_loyalty_points(company_id, client_id)
        print(f"Loyalty Points:\n{points_msg}")

        # 2. Redeem Points (Likely fail due to low balance if just converted, or succeed if rich)
        redeem_msg = redeem_loyalty_points(company_id, client_id, 100)
        print(f"Redeem 100 Points Result: {redeem_msg}")

    except Exception as e:
        print(f"Verification Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_refactor()
