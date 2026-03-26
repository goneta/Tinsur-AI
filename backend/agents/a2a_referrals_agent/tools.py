
from google.adk.tools import tool
from app.core.database import SessionLocal
from app.services.referral_service import ReferralService
import uuid

@tool
def get_referral_info(company_id: str, client_id: str) -> str:
    """
    Retrieves referral information for a specific client, including their code and status of referrals.
    Args:
        company_id: The UUID of the company.
        client_id: The UUID of the client.
    """
    db = SessionLocal()
    try:
        service = ReferralService(db)
        referrals = service.get_client_referrals(
            company_id=uuid.UUID(company_id), 
            client_id=uuid.UUID(client_id)
        )
        
        if not referrals:
            return f"No referral records found for client {client_id} in company {company_id}. Use create_referral_link to generate one."
        
        # Summary matches original output format
        codes = list(set([r.referral_code for r in referrals]))
        total = len(referrals)
        converted = len([r for r in referrals if r.status == 'converted'])
        pending = len([r for r in referrals if r.status == 'pending'])
        
        return (f"Referral Info for Client {client_id}:\n"
                f"- Active Codes: {', '.join(codes)}\n"
                f"- Total Referrals: {total}\n"
                f"- Converted (Successful): {converted}\n"
                f"- Pending: {pending}")
    except Exception as e:
        return f"Error retrieving referral info: {str(e)}"
    finally:
        db.close()

@tool
def create_referral_link(company_id: str, client_id: str) -> str:
    """
    Generates a new unique referral code for a client.
    Args:
        company_id: The UUID of the company.
        client_id: The UUID of the client.
    """
    db = SessionLocal()
    try:
        service = ReferralService(db)
        referral = service.create_referral(
            company_id=uuid.UUID(company_id),
            referrer_client_id=uuid.UUID(client_id)
        )
        
        return f"Created new referral link! Your code is: {referral.referral_code}. Share it to earn rewards."
    except Exception as e:
        db.rollback() # Service commits, but safe to have rollback here just in case of other errors
        return f"Error creating referral link: {str(e)}"
    finally:
        db.close()
