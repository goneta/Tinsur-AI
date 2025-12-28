
import sys
import os
import uuid
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add parent directory to path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash

from app.models.company import Company
from app.models.user import User
from app.models.client import Client
from app.models.policy_type import PolicyType
from app.models.quote import Quote
from app.models.premium_policy import PremiumPolicyType, PremiumPolicyCriteria
from app.models.policy_service import PolicyService
from app.models.regulatory import IFRS17Group
from app.models.pos_location import POSLocation
from app.models.endorsement import Endorsement
from app.models.claim import Claim
from app.models.co_insurance import CoInsuranceShare

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_test_data():
    db = SessionLocal()
    try:
        logger.info("Starting database seeding for test data...")

        # 1. Get or Create Company
        company = db.query(Company).filter(Company.subdomain == "demoinsurance.com").first()
        if not company:
            company = Company(
                name="Demo Insurance Co",
                subdomain="demoinsurance.com",
                email="contact@demoinsurance.com",
                phone="123456789",
                is_active=True
            )
            db.add(company)
            db.flush()
            logger.info(f"Created Company: {company.name}")
        else:
            logger.info(f"Using existing Company: {company.name}")

        # 2. Get or Create Admin User
        admin = db.query(User).filter(User.email == "admin@demoinsurance.com").first()
        if not admin:
            admin = User(
                company_id=company.id,
                email="admin@demoinsurance.com",
                first_name="Admin",
                last_name="User",
                password_hash=get_password_hash("admin"), # Password is 'admin'
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.flush()
            logger.info(f"Created Admin User: {admin.email}")
        else:
             logger.info(f"Using existing Admin User: {admin.email}")

        # 3. Seed Policy Services
        services_data = [
            {"name_en": "Courtesy Car", "default_price": 50.00, "description": "Provision of a courtesy car while yours is being repaired."},
            {"name_en": "Windscreen Cover", "default_price": 25.00, "description": "Coverage for windscreen repair or replacement."},
            {"name_en": "Personal Accident Cover", "default_price": 15.00, "description": "Personal accident cover up to £5,000."},
            {"name_en": "No Claims Discount Protection", "default_price": 30.00, "description": "Protect your No Claims Discount even if you make a claim."},
            {"name_en": "Roadside Assistance", "default_price": 40.00, "description": "24/7 Roadside assistance."},
            {"name_en": "Legal Cover", "default_price": 20.00, "description": "Coverage for legal expenses."},
        ]

        seeded_services = []
        for svc in services_data:
            existing_svc = db.query(PolicyService).filter(
                PolicyService.company_id == company.id,
                PolicyService.name_en == svc["name_en"]
            ).first()
            
            if not existing_svc:
                new_svc = PolicyService(
                    company_id=company.id,
                    name_en=svc["name_en"],
                    default_price=svc["default_price"],
                    description=svc["description"],
                    is_active=True
                )
                db.add(new_svc)
                db.flush()
                seeded_services.append(new_svc)
                logger.info(f"Created Service: {svc['name_en']}")
            else:
                seeded_services.append(existing_svc)
                # Ensure it's in the current session if we fetched it
                logger.info(f"Existing Service: {svc['name_en']}")

        # 4. Seed Premium Policies and Criteria
        # Criteria
        criteria_defs = [
            {"name": "No Accidents", "field_name": "accidents_fault", "operator": "=", "value": "0"},
            {"name": "Low Car Age", "field_name": "car_age", "operator": "<", "value": "5"},
            {"name": "Low Mileage", "field_name": "mileage", "operator": "<", "value": "50000"},
            {"name": "Experienced Driver", "field_name": "license_years", "operator": ">=", "value": "5"},
        ]
        
        criteria_map = {}
        for c_data in criteria_defs:
            existing_crit = db.query(PremiumPolicyCriteria).filter(
                PremiumPolicyCriteria.company_id == company.id,
                PremiumPolicyCriteria.name == c_data["name"]
            ).first()
            
            if not existing_crit:
                new_crit = PremiumPolicyCriteria(
                    company_id=company.id,
                    name=c_data["name"],
                    field_name=c_data["field_name"],
                    operator=c_data["operator"],
                    value=c_data["value"]
                )
                db.add(new_crit)
                db.flush()
                criteria_map[c_data["name"]] = new_crit
                logger.info(f"Created Criteria: {c_data['name']}")
            else:
                criteria_map[c_data["name"]] = existing_crit

        # Premium Policy Types
        pp_defs = [
            {
                "name": "Premium Gold",
                "price": 500.00,
                "excess": 380.00,
                "criteria": ["No Accidents", "Low Car Age"],
                "services": ["Courtesy Car", "Windscreen Cover", "Personal Accident Cover"] # Names of services to link
            },
            {
                "name": "Safe Expert",
                "price": 400.00,
                "excess": 250.00,
                "criteria": ["No Accidents", "Experienced Driver"],
                "services": ["Roadside Assistance", "Legal Cover"]
            },
            {
                "name": "Full Comprehensive Plus",
                "price": 750.00,
                "excess": 100.00,
                "criteria": ["No Accidents"],
                "services": ["Courtesy Car", "Windscreen Cover", "Personal Accident Cover", "No Claims Discount Protection", "Roadside Assistance", "Legal Cover"]
            }
        ]

        for pp_data in pp_defs:
            existing_pp = db.query(PremiumPolicyType).filter(
                PremiumPolicyType.company_id == company.id,
                PremiumPolicyType.name == pp_data["name"]
            ).first()

            if not existing_pp:
                new_pp = PremiumPolicyType(
                    company_id=company.id,
                    name=pp_data["name"],
                    price=pp_data["price"],
                    excess=pp_data.get("excess", 0.00),
                    is_active=True
                )
                db.add(new_pp)
                db.flush()
                
                # Link Criteria
                for c_name in pp_data["criteria"]:
                    if c_name in criteria_map:
                        new_pp.criteria.append(criteria_map[c_name])
                
                # Link Services
                for s_name in pp_data["services"]:
                    svc_obj = next((s for s in seeded_services if s.name_en == s_name), None)
                    if svc_obj:
                         # Check if already linked (unlikely for new PP but good practice)
                         if svc_obj not in new_pp.services:
                            new_pp.services.append(svc_obj)
                
                logger.info(f"Created Premium Policy: {pp_data['name']} with services")
            else:
                # If exists, ensure services are linked (idempotency improvement)
                for s_name in pp_data["services"]:
                    svc_obj = next((s for s in seeded_services if s.name_en == s_name), None)
                    if svc_obj and svc_obj not in existing_pp.services:
                        existing_pp.services.append(svc_obj)
                        logger.info(f"Linked service {s_name} to existing policy {pp_data['name']}")
                logger.info(f"Processed Premium Policy: {pp_data['name']}")


        # 5. Seed Quotes
        # Ensure standard policy types exist for quotes
        pt_auto = db.query(PolicyType).filter(PolicyType.name.ilike("%auto%")).first()
        if not pt_auto:
            pt_auto = PolicyType(name="Automobile", code="AUTO", description="Auto Insurance")
            db.add(pt_auto)
            db.flush()

        pt_home = db.query(PolicyType).filter(PolicyType.name.ilike("%home%")).first()
        if not pt_home:
            pt_home = PolicyType(name="Home", code="HOME", description="Home Insurance")
            db.add(pt_home)
            db.flush()

        # Ensure a client exists
        client = db.query(Client).filter(Client.email == "test.client@example.com").first()
        if not client:
            client = Client(
                company_id=company.id,
                first_name="Test",
                last_name="Client",
                email="test.client@example.com",
                phone="555-123-4567",
                client_type="individual"
            )
            db.add(client)
            db.flush()

        quotes_data = [
            {
                "num": "Q-TEST-001", "pt": pt_auto, "status": "draft", "amount": 1200.00, 
                "apr": 5.0, "fees": 50.00, "extra": 25.00
            },
            {
                "num": "Q-TEST-002", "pt": pt_home, "status": "sent", "amount": 800.00, 
                "apr": 0.0, "fees": 20.00, "extra": 0.00
            },
            {
                "num": "Q-TEST-003", "pt": pt_auto, "status": "accepted", "amount": 1500.00, 
                "apr": 4.5, "fees": 50.00, "extra": 100.00
            },
             {
                "num": "Q-TEST-004", "pt": pt_home, "status": "draft", "amount": 2500.00, 
                "apr": 12.0, "fees": 150.00, "extra": 0.00
            },
        ]

        for q_d in quotes_data:
            existing_q = db.query(Quote).filter(Quote.quote_number == q_d["num"]).first()
            if not existing_q:
                # Calculate simple financials
                total_financed = Decimal(q_d["amount"]) + Decimal(q_d["fees"]) + Decimal(q_d["extra"])
                monthly = total_financed / 12 # simple calc
                
                new_q = Quote(
                    company_id=company.id,
                    client_id=client.id,
                    policy_type_id=q_d["pt"].id,
                    quote_number=q_d["num"],
                    status=q_d["status"],
                    premium_amount=q_d["amount"],
                    final_premium=q_d["amount"], # Simplification
                    coverage_amount=500000,
                    valid_until=date.today() + timedelta(days=30),
                    created_by=admin.id,
                    
                    # Financials
                    apr_percent=q_d["apr"],
                    arrangement_fee=q_d["fees"],
                    extra_fee=q_d["extra"],
                    total_financed_amount=total_financed,
                    monthly_installment=monthly,
                    total_installment_price=total_financed
                )
                db.add(new_q)
                logger.info(f"Created Quote: {q_d['num']}")
            else:
                 logger.info(f"Existing Quote: {q_d['num']}")


        db.commit()
        logger.info("Database seeding completed successfully!")

    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_test_data()
