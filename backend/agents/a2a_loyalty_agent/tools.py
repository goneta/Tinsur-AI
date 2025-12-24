
from google.adk.tools import tool
from app.core.database import SessionLocal
from app.models.loyalty import LoyaltyPoint
import uuid

@tool
def get_loyalty_points(company_id: str, client_id: str) -> str:
    """
    Retrieves the current loyalty points balance and tier for a specific client.
    Args:
        company_id: The UUID of the company.
        client_id: The UUID of the client.
    """
    db = SessionLocal()
    try:
        loyalty = db.query(LoyaltyPoint).filter(
            LoyaltyPoint.company_id == uuid.UUID(company_id),
            LoyaltyPoint.client_id == uuid.UUID(client_id)
        ).first()
        if not loyalty:
            return f"No loyalty account found for client {client_id} in company {company_id}."
        
        return (f"Loyalty Account for Client {client_id}:\n"
                f"- Balance: {loyalty.points_balance} points\n"
                f"- Earned: {loyalty.points_earned} points\n"
                f"- Redeemed: {loyalty.points_redeemed} points\n"
                f"- Current Tier: {loyalty.tier}")
    except Exception as e:
        return f"Error retrieving loyalty points: {str(e)}"
    finally:
        db.close()

@tool
def redeem_loyalty_points(company_id: str, client_id: str, points_to_redeem: int) -> str:
    """
    Redeems a specified amount of loyalty points for a client.
    Args:
        company_id: The UUID of the company.
        client_id: The UUID of the client.
        points_to_redeem: The number of points to redeem.
    """
    db = SessionLocal()
    try:
        loyalty = db.query(LoyaltyPoint).filter(
            LoyaltyPoint.company_id == uuid.UUID(company_id),
            LoyaltyPoint.client_id == uuid.UUID(client_id)
        ).first()
        if not loyalty:
            return f"Error: No loyalty account found for client {client_id} in company {company_id}."
        
        if loyalty.points_balance < points_to_redeem:
            return f"Error: Insufficient balance. Available: {loyalty.points_balance}, Attempted: {points_to_redeem}."
        
        loyalty.points_balance -= points_to_redeem
        loyalty.points_redeemed += points_to_redeem
        db.commit()
        
        return f"Successfully redeemed {points_to_redeem} points. New balance: {loyalty.points_balance}."
    except Exception as e:
        db.rollback()
        return f"Error redeeming points: {str(e)}"
    finally:
        db.close()
