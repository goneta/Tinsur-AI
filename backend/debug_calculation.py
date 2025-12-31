
import sys
import os
import logging
from decimal import Decimal
from uuid import uuid4

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.quote_service import QuoteService
from app.repositories.quote_repository import QuoteRepository
from app.core.database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_calculation():
    db = SessionLocal()
    try:
        repo = QuoteRepository(db)
        service = QuoteService(repo)
        
        # Mock Data
        risk_factors = {
            "driver_age": 30,
            "vehicle_value": 5000000,
            "accidents": 0
        }
        
        # Test Case 1: Basic
        logger.info("Test 1: Basic Calculation")
        result = service.calculate_premium(
            risk_factors=risk_factors,
            duration_months=12,
            financial_overrides=None,
            policy_type_id=uuid4(),
            coverage_amount=Decimal("1000000")
        )
        print("Result 1:", result)
        
        # Test Case 2: Finanical Overrides (Fees & Tax)
        logger.info("Test 2: With Overrides")
        overrides = {
            "fixed_fee": [1000, 500],
            "government_tax": 18,
            "company_discount": 5,
            "risk_multiplier": 1.5
        }
        result = service.calculate_premium(
            risk_factors=risk_factors,
            duration_months=12,
            financial_overrides=overrides,
            policy_type_id=uuid4(),
            coverage_amount=Decimal("1000000")
        )
        print("Result 2:", result)

    except Exception as e:
        logger.error(f"Calculation Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_calculation()
