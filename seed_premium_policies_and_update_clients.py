import sys
import os
import random
from datetime import date, timedelta
from decimal import Decimal

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Change CWD to backend so sqlite:///./insurance.db resolves correctly
os.chdir(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal
from app.models.company import Company
from app.models.premium_policy import PremiumPolicyType, PremiumPolicyCriteria
from app.models.policy_service import PolicyService
from app.models.client import Client

def seed_premium_policies():
    db = SessionLocal()
    try:
        # 1. Get Company
        company = db.query(Company).first()
        if not company:
            print("No company found! Run seed_data.py first.")
            return
        
        print(f"Seeding for Company: {company.name}")
        cid = company.id

        # 2. Clear existing Premium Policy Types & Criteria & Services
        # (This cleans up previous seeding to ensure fresh state)
        print("Clearing old Premium Policy data...")
        db.query(PremiumPolicyCriteria).filter_by(company_id=cid).delete()
        db.query(PremiumPolicyType).filter_by(company_id=cid).delete()
        db.query(PolicyService).filter_by(company_id=cid).delete()
        db.commit()

        # 3. Create Services
        print("Creating Policy Services...")
        svc_roadside = PolicyService(
            company_id=cid,
            name_en="Roadside Assistance",
            name_fr="Assistance Routière",
            description="24/7 towing and roadside help.",
            default_price=15000,
            category="Assistance",
            icon_name="TowTruck"
        )
        svc_glass = PolicyService(
            company_id=cid,
            name_en="Glass Coverage",
            name_fr="Bris de Glace",
            description="Coverage for windscreen and window damage.",
            default_price=10000,
            category="Protection",
            icon_name="Shield"
        )
        svc_medical = PolicyService(
            company_id=cid,
            name_en="Personal Accident",
            name_fr="Individuelle Accident",
            description="Medical expenses for driver and passengers.",
            default_price=25000,
            category="Medical",
            icon_name="HeartPulse"
        )
        
        db.add_all([svc_roadside, svc_glass, svc_medical])
        db.commit()
        
        # Refresh to get IDs
        db.refresh(svc_roadside)
        db.refresh(svc_glass)
        db.refresh(svc_medical)

        # 4. Create Policy Types
        print("Creating Premium Policy Types...")

        # -- GOLD --
        # Requires Age >= 25
        gold = PremiumPolicyType(
            company_id=cid,
            name="Gold Comprehensive",
            description="Full coverage with low excess and all perks included.",
            price=500000,
            excess=50000,
            tagline="Best Value",
            is_featured=True,
            is_active=True
        )
        
        # -- SILVER --
        # Requires Age >= 21
        silver = PremiumPolicyType(
            company_id=cid,
            name="Silver Standard",
            description="Balanced coverage for everyday drivers.",
            price=300000,
            excess=75000,
            tagline="Popular",
            is_featured=False,
            is_active=True
        )

        # -- BRONZE --
        # Requires Age >= 18
        bronze = PremiumPolicyType(
            company_id=cid,
            name="Bronze Basic",
            description="Essential third-party liability coverage.",
            price=100000,
            excess=100000,
            tagline="Economy",
            is_featured=False,
            is_active=True
        )

        db.add_all([gold, silver, bronze])
        db.commit()
        
        db.refresh(gold)
        db.refresh(silver)
        db.refresh(bronze)

        # Link Services
        # Gold gets all, Silver gets Roadside, Bronze gets none included (available as add-on usually logic depends on frontend/backend)
        # Note: The association table 'premium_policy_service_association' determines "Included" services usually?
        # Let's assume these are "Included Services" for the policy type.
        gold.services.append(svc_roadside)
        gold.services.append(svc_glass)
        gold.services.append(svc_medical)
        
        silver.services.append(svc_roadside)
        
        db.commit()

        # 5. Create Criteria
        print("Creating Eligibility Criteria...")
        
        crit_age_25 = PremiumPolicyCriteria(
            company_id=cid,
            name="Minimum Age 25",
            description="Must be at least 25 years old",
            field_name="age",
            operator=">=",
            value="25"
        )
        
        crit_age_21 = PremiumPolicyCriteria(
            company_id=cid,
            name="Minimum Age 21",
            description="Must be at least 21 years old",
            field_name="age",
            operator=">=",
            value="21"
        )
        
        crit_age_18 = PremiumPolicyCriteria(
            company_id=cid,
            name="Minimum Age 18",
            description="Must be at least 18 years old",
            field_name="age",
            operator=">=",
            value="18"
        )
        
        db.add_all([crit_age_25, crit_age_21, crit_age_18])
        db.commit()
        
        # Link Criteria to Policy Types using the 'criteria' relationship
        gold.criteria.append(crit_age_25)
        silver.criteria.append(crit_age_21)
        bronze.criteria.append(crit_age_18)
        
        db.commit()

        # 6. Update Clients
        print("Updating Clients to ensure eligibility...")
        clients = db.query(Client).all()
        count = 0
        
        # We will distribute ages so we can test different eligibility
        # 0: Age 30 (Eligible for all)
        # 1: Age 22 (Eligible for Silver, Bronze)
        # 2: Age 19 (Eligible for Bronze only)
        
        for i, client in enumerate(clients):
            updated = False
            
            # Set DOB map
            remainder = i % 3
            if remainder == 0:
                # Age ~35 (1990)
                target_dob = date(1990, 5, 20)
            elif remainder == 1:
                # Age ~23 (2002) - wait, 2026-2002 = 24. Let's start from 2003 -> 23.
                target_dob = date(2003, 8, 15)
            else:
                # Age ~19 (2007) - 2026-2007 = 19.
                target_dob = date(2007, 1, 10)
                
            if not client.date_of_birth or client.date_of_birth != target_dob:
                client.date_of_birth = target_dob
                updated = True
            
            # Ensure other fields required by schemas or logic
            if not client.country:
                client.country = "Côte d'Ivoire"
                updated = True
            
            if not client.risk_profile:
                client.risk_profile = "medium"
                updated = True
                
            if not client.client_type:
                client.client_type = "individual"
                updated = True
                
            if updated:
                count += 1
                
        db.commit()
        print(f"Updated {count} clients with valid DOBs and Profile data.")
        print("Seeding Complete!")

    except Exception as e:
        print(f"Error seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_premium_policies()
