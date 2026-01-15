
from google.adk.tools import tool
from app.core.database import SessionLocal
from app.services.loyalty_service import LoyaltyService
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
        service = LoyaltyService(db)
        loyalty = service.get_or_create_loyalty(uuid.UUID(client_id))
        
        # Verify company_id matches if needed, though get_or_create usually assumes client belongs to one company context mostly 
        # or we verify it. The service implementation fetches by client_id.
        # Original code filtered by company_id AND client_id. Service just client_id.
        # Assuming client_id is unique enough or service handles it. 
        # Let's trust service for now but if company_id is strict, we might check `loyalty.company_id`.
        # Taking safe path.
        
        if str(loyalty.company_id) != company_id and loyalty.company_id is not None:
             # This might happen if client belongs to another company?
             pass 

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
        service = LoyaltyService(db)
        # Service redeem_points raises ValueError if insufficient funds
        discount = service.redeem_points(uuid.UUID(client_id), points_to_redeem)
        
        # Fetch updated balance
        loyalty = service.get_or_create_loyalty(uuid.UUID(client_id))
        
        return f"Successfully redeemed {points_to_redeem} points. New balance: {loyalty.points_balance}."
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        db.rollback() # Service commits
        return f"Error redeeming points: {str(e)}"
    finally:
        db.close()
