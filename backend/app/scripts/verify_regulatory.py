
import sys
import os
from decimal import Decimal
from datetime import date
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal, engine, Base
from app.models.regulatory import IFRS17Group, RegulatoryMetricSnapshot
from app.models.company import Company
from app.services.regulatory_service import RegulatoryService
from app.services.accounting_service import AccountingService

async def verify_regulatory_flow():
    print("Ensuring Regulatory tables exist...")
    Base.metadata.create_all(bind=engine)
    
    print("Verifying Regulatory & Solvency Flow...")
    db = SessionLocal()
    try:
        company = db.query(Company).first()
        if not company:
            print("No company found for testing.")
            return

        print(f"Testing for Company: {company.name}")
        
        # 1. Initialize Accounts (Ensures Equity exists for Own Funds)
        acc_service = AccountingService(db)
        acc_service.initialize_chart_of_accounts(company.id)
        
        # 2. Test Solvency Calculation
        reg_service = RegulatoryService(db)
        print("Calculating Solvency Ratio...")
        solvency = reg_service.calculate_solvency_ratio(company.id)
        
        print(f"Solvency Ratio: {solvency['solvency_ratio']:.2f}")
        print(f"Status: {solvency['status']}")
        
        # 3. Test IFRS 17 CSM Amortization
        print("\nTesting IFRS 17 CSM Amortization...")
        # Create a test group
        group = IFRS17Group(
            company_id=company.id,
            name="Test Motor Group 2025",
            initial_csm=Decimal("12000.00"),
            remaining_csm=Decimal("12000.00"),
            cohort_year="2025",
            portfolio="Motor",
            profitability_category="other"
        )
        db.add(group)
        db.commit()
        
        print(f"Group Created: {group.name}, CSM: {group.initial_csm}")
        
        released = reg_service.amortize_csm(group.id)
        print(f"Amortized Amount: {released}")
        
        # Refresh and check
        db.refresh(group)
        print(f"Remaining CSM: {group.remaining_csm}")
        
        if abs(group.remaining_csm - Decimal("11000.00")) < 0.01:
            print("SUCCESS: CSM correctly amortized (1/12th of 12000).")
        else:
            print(f"ERROR: CSM mismatch. Expected 11000, got {group.remaining_csm}")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(verify_regulatory_flow())
