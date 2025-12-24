
from google.adk.tools import tool
from app.core.database import SessionLocal
from app.models.referral import Referral
import uuid
import random
import string

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
        # Get referrals initiated by this client in this company
        referrals = db.query(Referral).filter(
            Referral.company_id == uuid.UUID(company_id),
            Referral.referrer_client_id == uuid.UUID(client_id)
        ).all()
        
        if not referrals:
            return f"No referral records found for client {client_id} in company {company_id}. Use create_referral_link to generate one."
        
        # Summary
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
        # Check if already has a code in this company
        existing = db.query(Referral).filter(
            Referral.company_id == uuid.UUID(company_id),
            Referral.referrer_client_id == uuid.UUID(client_id)
        ).first()
        if existing:
            return f"Client already has an active referral code in this company: {existing.referral_code}"
            
        # Generate random code
        new_code = "REF-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        new_referral = Referral(
            company_id=uuid.UUID(company_id),
            referrer_client_id=uuid.UUID(client_id),
            referral_code=new_code,
            status='pending',
            reward_amount=5000.0, # Default reward
            reward_paid=False
        )
        db.add(new_referral)
        db.commit()
        
        return f"Created new referral link! Your code is: {new_code}. Share it to earn rewards."
    except Exception as e:
        db.rollback()
        return f"Error creating referral link: {str(e)}"
    finally:
        db.close()
