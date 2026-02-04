import sys
import os
from decimal import Decimal
from uuid import uuid4

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.quote_service import QuoteService
from app.models.company import Company
from app.models.quote import Quote
from app.models.client import Client
from unittest.mock import MagicMock

def test_calculation():
    # Mock Repository and DB
    mock_db = MagicMock()
    mock_repo = MagicMock()
    mock_repo.db = mock_db
    
    service = QuoteService(mock_repo)
    
    company_id = uuid4()
    
    # Step 1: Mock Company with specifically chosen rates
    mock_company = Company(
        id=company_id,
        admin_fee_percent=10.0,      # F = 10%
        admin_discount_percent=5.0,  # D = 5%
        government_tax_percent=15.0, # T = 15%
        apr_percent=0.0,
        arrangement_fee=0.0
    )
    
    # Setup mock query for company
    mock_db.query.return_value.filter.return_value.first.return_value = mock_company
    
    # Parameters
    risk_factors = {"driver_age": 30, "accidents": 0} # Should result in score 45 or something, but let's see
    # In service: Base 50, Age 30 -> -5, Accidents 0 -> +0. Total score = 45.
    
    # We want to verify: ((P + (P * F) + S) * (1 - D)) * (1 + T)
    # Let's fix P by setting base_rate and coverage or using financial_overrides
    
    financial_overrides = {
        "base_rate": 10.0, # 10% rate
    }
    # coverage_amount = 10000 -> base_premium = 1000
    # extra_fee (services) = 200
    
    # Mock selected services to add to extra_fee
    # Actually, let's just use fixed_fee override if possible or mock the policy service query
    # In calculate_premium, extra_fee starts at 0, then adds from company.extra_fee, then financial_overrides['fixed_fee'], then services.
    
    financial_overrides["fixed_fee"] = 200 # This will be our 'S'
    
    result = service.calculate_premium(
        risk_factors=risk_factors,
        coverage_amount=Decimal('10000'),
        company_id=company_id,
        financial_overrides=financial_overrides,
        duration_months=12
    )
    
    # Manual Calculation:
    # 1. base_rate = 10% of 10000 = 1000
    # 2. total_risk_adjustment: 
    #    risk_score = 45 (Base 50 - Age 5)
    #    score_cost = 1000 * 0.45 = 450
    #    total_risk_adjustment = 450
    # 3. P (p_foundation) = 1000 + 450 = 1450
    # 4. Step 2: Admin Fee = 1450 * 10% = 145
    #    Subtotal1 = 1450 + 145 = 1595
    # 5. Step 3: Services (S) = 200
    #    Subtotal2 = 1595 + 200 = 1795
    # 6. Step 4: Admin Discount = 1795 * 5% = 89.75
    #    Subtotal3 = 1795 - 89.75 = 1705.25
    # 7. Step 5: Tax = 1705.25 * 15% = 255.7875 -> 255.7875
    #    Final = 1705.25 + 255.7875 = 1961.0375
    #    Rounded = 1961.04
    
    print(f"Base Premium: {result['base_premium']}")
    print(f"Risk Adjustment: {result['risk_adjustment']}")
    print(f"Admin Fee Amount: {result['admin_fee']}")
    print(f"Extra Fee (Services): {result['extra_fee']}")
    print(f"Discount Amount: {result['discount_amount']}")
    print(f"Tax Amount: {result['tax_amount']}")
    print(f"Final Premium: {result['final_premium']}")
    print(f"Breakdown: {result['calculation_breakdown']}")
    
    # Assertions
    expected_final = Decimal('1961.04')
    assert result['final_premium'] == expected_final, f"Expected {expected_final}, got {result['final_premium']}"
    
    # Check breakdown steps
    breakdown = result['calculation_breakdown']
    assert breakdown['step1_base_premium'] == 1450.0
    assert breakdown['step2_admin_fee']['amount'] == 145.0
    assert breakdown['step3_services']['amount'] == 200.0
    assert breakdown['step4_admin_discount']['amount'] == 89.75
    
    print("Test passed successfully!")

if __name__ == "__main__":
    test_calculation()
