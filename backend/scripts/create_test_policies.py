from app.core.database import SessionLocal
from app.models.policy import Policy
from app.models.company import Company
from app.models.premium_policy import PremiumPolicyType
from datetime import datetime, timedelta
import uuid
import traceback

def create_test_policies():
    db = SessionLocal()
    client_uuid = uuid.UUID('73a5a9e9-4211-464a-b392-08a64c793817')
    company = db.query(Company).first()
    policy_type = db.query(PremiumPolicyType).first()
    
    if not company or not policy_type:
        print("Required base data (Company or PolicyType) missing.")
        return

    admin_user_id = uuid.UUID('bf448f88-fde2-48f4-97eb-ba8d189b6c4e')

    policies_to_create = [
        {
            'num': 'POL-TEST-BMW-001', 
            'veh': {'make': 'BMW', 'model': '3 Series', 'registration': 'BMW-001-TEST', 'year': 2022}, 
            'days': 365,
            'policy_type_name': 'BMW Performance Cover'
        },
        {
            'num': 'POL-TEST-AUDI-002', 
            'veh': {'make': 'Audi', 'model': 'A4', 'registration': 'AUDI-002-TEST', 'year': 2021}, 
            'days': 180,
            'policy_type_name': 'Audi Executive Plan'
        },
        {
            'num': 'POL-TEST-TSLA-003', 
            'veh': {'make': 'Tesla', 'model': 'Model 3', 'registration': 'TSLA-003-TEST', 'year': 2023}, 
            'days': 90,
            'policy_type_name': 'Tesla Smart Eco'
        }
    ]

    for p in policies_to_create:
        # Check if already exists
        exists = db.query(Policy).filter(Policy.policy_number == p['num']).first()
        if exists:
            print(f"Policy {p['num']} already exists.")
            continue

        new_p = Policy(
            id=uuid.uuid4(),
            company_id=company.id,
            client_id=client_uuid,
            policy_type_id=policy_type.id,
            policy_number=p['num'],
            premium_amount=1200.0,
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=p['days'])).date(),
            status='active',
            created_by=admin_user_id,
            details={
                'vehicles': [p['veh']],
                'cover_type': 'Comprehensive',
                'drivers': [{'name': 'Test User', 'type': 'Main'}],
                'voluntary_excess': 250,
                'compulsory_excess': 200,
                'policy_type_name': p['policy_type_name']
            }
        )
        db.add(new_p)
        print(f"Created policy object for: {p['num']}")
    
    try:
        db.commit()
        print("Success: Test policies setup complete.")
    except Exception as e:
        db.rollback()
        print(f"Error during commit: {str(e)}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_policies()
