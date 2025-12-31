
import sys
import os
import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.company import Company
from app.models.user import User
from app.models.client import Client
from app.models.premium_policy import PremiumPolicyType, PremiumPolicyCriteria
from app.models.quote_element import QuoteElement

def seed_full_wizard_data():
    db = SessionLocal()
    try:
        print("Starting Full Quote Wizard Seeding...")

        # 1. Company
        company = db.query(Company).filter(Company.subdomain == "demoinsurance.com").first()
        if not company:
            # Try finding by email
            company = db.query(Company).filter(Company.email == "admin@demoinsurance.com").first()
        
        if not company:
            print("Creating Demo Company...")
            company = Company(
                name="Demo Insurance Co",
                subdomain="demoinsurance.com",
                email="admin@demoinsurance.com",
                country="Ivory Coast",
                currency="XOF"
            )
            db.add(company)
            db.commit()
            db.refresh(company)
        else:
            print(f"Using Company: {company.name}")

        # 2. Clients (Goldie, Silver)
        print("Seeding Clients...")
        clients_data = [
            {
                "email": "gold.driver@example.com",
                "fname": "Goldie", "lname": "Driver",
                "risk_profile": "low",
                "fields": {"accident_count": 0, "no_claims_years": 5, "driving_license_years": 8, "employment_status": "Employed"}
            },
            {
                "email": "silver.driver@example.com", 
                "fname": "Silver", "lname": "Surfer",
                "risk_profile": "medium",
                "fields": {"accident_count": 0, "no_claims_years": 0, "driving_license_years": 1, "employment_status": "Student"}
            }
        ]

        for c_data in clients_data:
            user = db.query(User).filter(User.email == c_data["email"]).first()
            if not user:
                user = User(
                    company_id=company.id,
                    email=c_data["email"],
                    password_hash=get_password_hash("password123"),
                    first_name=c_data["fname"],
                    last_name=c_data["lname"],
                    role="client",
                    is_active=True,
                    is_verified=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            client = db.query(Client).filter(Client.email == c_data["email"]).first()
            if not client:
                client = Client(
                    company_id=company.id,
                    user_id=user.id,
                    first_name=c_data["fname"],
                    last_name=c_data["lname"],
                    email=c_data["email"],
                    client_type="individual",
                    status="active",
                    risk_profile=c_data["risk_profile"],
                    # Populate specific eligibility fields into appropriate columns if they exist
                    # Assuming Client model has these or we put them in details
                    accident_count=c_data["fields"]["accident_count"],
                    no_claims_years=c_data["fields"]["no_claims_years"],
                    driving_license_years=c_data["fields"]["driving_license_years"],
                    employment_status=c_data["fields"]["employment_status"]
                )
                db.add(client)
                print(f"Created Client: {c_data['fname']}")
            else:
                # Update fields just in case
                client.accident_count = c_data["fields"]["accident_count"]
                client.driving_license_years = c_data["fields"]["driving_license_years"]
                print(f"Updated Client: {c_data['fname']}")
        db.commit()

        # 3. Premium Policies
        print("Seeding Premium Policies...")
        # (Simplified logic from seed_premium_policies.py)
        # We need Criteria first
        criteria_defs = [
            {"name": "No Accidents", "field": "accident_count", "op": "=", "val": "0"},
            {"name": "Min License 5yrs", "field": "driving_license_years", "op": ">=", "val": "5"},
            {"name": "Employed Status", "field": "employment_status", "op": "=", "val": "Employed"}
        ]
        
        crit_map = {}
        for c in criteria_defs:
            crit = db.query(PremiumPolicyCriteria).filter(PremiumPolicyCriteria.name == c["name"]).first()
            if not crit:
                crit = PremiumPolicyCriteria(
                    company_id=company.id,
                    name=c["name"],
                    field_name=c["field"],
                    operator=c["op"],
                    value=c["val"]
                )
                db.add(crit)
                db.commit()
            crit_map[c["name"]] = crit

        # Policy Types
        policies = [
            {"name": "Gold Driver", "price": 50000, "criteria": ["No Accidents", "Min License 5yrs"]},
            {"name": "Standard Driver", "price": 35000, "criteria": ["No Accidents"]},
            {"name": "Starter", "price": 60000, "criteria": []}
        ]

        for p in policies:
            pol = db.query(PremiumPolicyType).filter(PremiumPolicyType.name == p["name"]).first()
            if not pol:
                pol = PremiumPolicyType(
                    company_id=company.id,
                    name=p["name"],
                    price=p["price"],
                    is_active=True
                )
                db.add(pol)
                db.commit()
                # Add criteria
                for c_name in p["criteria"]:
                    if c_name in crit_map:
                         # Append via relationship or secondary table
                         # Assuming mapping exists, but let's do direct SQL for safety if relation issue
                         stmt = text("INSERT INTO premium_policy_type_criteria (policy_type_id, criteria_id) VALUES (:pid, :cid)")
                         try:
                            # Check if exists first
                            pass # Simplification: relationships handles duplicate check usually?
                            pol.criteria.append(crit_map[c_name])
                         except:
                            pass
                db.commit()
                print(f"Created Policy: {p['name']}")

        # 4. Quote Elements (ALL types)
        print("Seeding Quote Elements...")
        elements = [
            # Base Rates
            {"category": "base_rate", "name": "Standard Rate", "value": 3.5, "desc": "Standard 3.5% Base Rate"},
            {"category": "base_rate", "name": "Premium Rate", "value": 5.0, "desc": "Premium 5% Base Rate"},
            
            # Coverage Amounts
            {"category": "coverage_amount", "name": "Basic Coverage", "value": 5000000, "desc": "5M coverage"},
            {"category": "coverage_amount", "name": "Standard Coverage", "value": 10000000, "desc": "10M coverage"},
            {"category": "coverage_amount", "name": "Premium Coverage", "value": 25000000, "desc": "25M coverage"},
            
            # Risk Multipliers
            {"category": "risk_multiplier", "name": "Young Driver (<25)", "value": 1.25, "desc": "+25% Risk"},
            {"category": "risk_multiplier", "name": "Sports Car", "value": 1.50, "desc": "+50% Risk"},
            {"category": "risk_multiplier", "name": "Urban Area", "value": 1.10, "desc": "+10% Risk"},
            
            # Fixed Fees
            {"category": "fixed_fee", "name": "Admin Fee", "value": 5000, "desc": "Processing fee"},
            {"category": "fixed_fee", "name": "Policy Setup", "value": 2500, "desc": "One-time setup"},
            
            # Government Tax (NEW)
            {"category": "government_tax", "name": "VAT", "value": 18.0, "desc": "Standard VAT 18%"},
            {"category": "government_tax", "name": "Insurance Levy", "value": 2.5, "desc": "Statutory Levy"},
            
            # Company Discount (NEW)
            {"category": "company_discount", "name": "Employee Discount", "value": 15.0, "desc": "15% Staff Discount"},
            {"category": "company_discount", "name": "Loyalty Bonus", "value": 5.0, "desc": "5% Renewal Bonus"},
        ]

        count = 0
        for e in elements:
            exists = db.query(QuoteElement).filter(
                QuoteElement.company_id == company.id, 
                QuoteElement.name == e["name"],
                QuoteElement.category == e["category"]
            ).first()
            if not exists:
                el = QuoteElement(
                    company_id=company.id,
                    category=e["category"],
                    name=e["name"],
                    value=Decimal(str(e["value"])),
                    description=e["desc"],
                    is_active=True
                )
                db.add(el)
                count += 1
        
        db.commit()
        print(f"Seeded {count} new Quote Elements.")

        print("\nSeeding Complete! Database ready for Quote Wizard.")

    except Exception as ex:
        print(f"Error: {ex}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_full_wizard_data()
