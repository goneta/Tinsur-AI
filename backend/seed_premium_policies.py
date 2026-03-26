import sys
import os
import uuid
from decimal import Decimal
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.models.premium_policy import PremiumPolicyType, PremiumPolicyCriteria, premium_policy_type_criteria
from app.models.company import Company
# Import other models to ensure mappers are initialized
from app.models.policy_service import PolicyService
from app.models.user import User
from app.models.client import Client
from app.models.policy import Policy
from app.models.endorsement import Endorsement
from app.models.regulatory import IFRS17Group

def seed_premium_policies():
    db = SessionLocal()
    try:
        # Get demo company
        company = db.query(Company).filter(Company.subdomain == "demoinsurance.com").first()
        if not company:
            print("Company not found, please run create_admin_user.py first.")
            return

        print(f"Seeding Premium Policies for {company.name}...")

        # 1. Create Criteria
        criteria_defs = [
            {"name": "No Accidents", "field_name": "accidents_fault", "operator": "=", "value": "0"},
            {"name": "Low Car Age", "field_name": "car_age", "operator": "<", "value": "5"},
            {"name": "Low Mileage", "field_name": "mileage", "operator": "<", "value": "50000"},
            {"name": "Experienced Driver", "field_name": "license_years", "operator": ">=", "value": "5"},
        ]

        criteria_map = {}
        for c_data in criteria_defs:
            existing = db.query(PremiumPolicyCriteria).filter(
                PremiumPolicyCriteria.company_id == company.id,
                PremiumPolicyCriteria.name == c_data["name"]
            ).first()
            if not existing:
                criteria = PremiumPolicyCriteria(
                    company_id=company.id,
                    name=c_data["name"],
                    field_name=c_data["field_name"],
                    operator=c_data["operator"],
                    value=c_data["value"]
                )
                db.add(criteria)
                db.flush()
                criteria_map[c_data["name"]] = criteria
            else:
                criteria_map[c_data["name"]] = existing

        # 2. Create Policy Types
        policy_defs = [
            {
                "name": "Bronze",
                "price": 159.01,
                "criteria": ["Experienced Driver"],
                "services": ["Comprehensive cover", "Small courtesy car", "Windscreen cover"]
            },
            {
                "name": "Silver",
                "price": 189.00,
                "criteria": ["No Accidents", "Experienced Driver"],
                "services": [
                    "Comprehensive cover", "Small courtesy car", "Windscreen cover",
                    "90-day comprehensive EU cover", "Uninsured driver promise", "Claims portal access"
                ]
            },
            {
                "name": "Gold",
                "price": 245.00,
                "criteria": ["No Accidents", "Low Car Age", "Low Mileage"],
                "services": [
                    "Comprehensive cover", "Small courtesy car", "Upgraded courtesy car", 
                    "90-day comprehensive EU cover", "Windscreen cover", "Uninsured driver promise",
                    "Loss of keys", "Claims portal access", "Personal accident cover",
                    "Personal belongings cover", "Manufacturer-fitted audio equipment / sat nav",
                    "Audio equipment / sat nav", "Driving other cars (conditional)",
                    "Car seats cover", "Theft of keys", "New car replacement",
                    "Misfuelling cover", "Onward travel", "Vandalism promise", "Hotel expenses"
                ]
            }
        ]

        for p_data in policy_defs:
            existing = db.query(PremiumPolicyType).filter(
                PremiumPolicyType.company_id == company.id,
                PremiumPolicyType.name == p_data["name"]
            ).first()
            
            if not existing:
                policy = PremiumPolicyType(
                    company_id=company.id,
                    name=p_data["name"],
                    price=p_data["price"],
                    is_active=True
                )
                db.add(policy)
                db.flush()
                
                # Add criteria
                for c_name in p_data["criteria"]:
                    if c_name in criteria_map:
                        policy.criteria.append(criteria_map[c_name])
                
                # Add services
                if "services" in p_data:
                    for s_name in p_data["services"]:
                        service = db.query(PolicyService).filter(
                            PolicyService.company_id == company.id,
                            PolicyService.name_en == s_name
                        ).first()
                        if service:
                            policy.services.append(service)
            else:
                print(f"Policy {p_data['name']} already exists. Updating services...")
                # Update existing services if needed
                if "services" in p_data:
                    for s_name in p_data["services"]:
                        service = db.query(PolicyService).filter(
                            PolicyService.company_id == company.id,
                            PolicyService.name_en == s_name
                        ).first()
                        if service and service not in existing.services:
                            existing.services.append(service)

        db.commit()
        print("Premium Policies Seed Completed.")

    except Exception as e:
        print(f"Error seeding policies: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_premium_policies()
