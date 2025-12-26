
import sys
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
from typing import List

# Ensure we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from faker import Faker

from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash

# Import Models
from app.models.company import Company
from app.models.user import User
from app.models.client import Client
from app.models.policy_type import PolicyType
from app.models.policy_service import PolicyService
from app.models.pos_location import POSLocation
from app.models.regulatory import IFRS17Group
from app.models.endorsement import Endorsement
from app.models.co_insurance import CoInsuranceShare
from app.models.quote import Quote
from app.models.policy import Policy
from app.models.claim import Claim
from app.models.payment import Payment, PaymentTransaction
from app.models.document import Document, DocumentLabel

fake = Faker()

# Constants
ADMIN_EMAIL = "admin@demoinsurance.com"
PASSWORD = "Password123!"  # Common password for all seeded users

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_company(db: Session) -> Company:
    print("Seeding Company...")
    company = db.query(Company).filter(Company.email == ADMIN_EMAIL).first()
    if not company:
        company = Company(
            name="Demo Insurance Co",
            subdomain="demo",
            email=ADMIN_EMAIL,
            phone=fake.phone_number(),
            address=fake.address(),
            country="Côte d'Ivoire",
            currency="XOF"
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        print(f"Created Company: {company.name}")
    else:
        print(f"Using existing Company: {company.name}")
    return company

def seed_admin(db: Session, company: Company) -> User:
    print("Seeding Admin...")
    user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if not user:
        user = User(
            company_id=company.id,
            email=ADMIN_EMAIL,
            password_hash=get_password_hash(PASSWORD),
            first_name="Super",
            last_name="Admin",
            role="super_admin",
            is_active=True,
            is_verified=True,
            phone=fake.phone_number()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created Admin: {user.email}")
    else:
        # Ensure admin is active and has correct role
        user.is_active = True
        user.is_verified = True
        if user.role != 'super_admin':
            user.role = 'super_admin'
        db.commit()
        print(f"Verified Admin: {user.email}")
    return user

def seed_users(db: Session, company: Company) -> List[User]:
    print("Seeding Users...")
    roles = ['manager', 'agent', 'employee', 'client']
    users = []
    
    # Ensure at least 5 of each role
    for role in roles:
        current_count = db.query(User).filter(User.company_id == company.id, User.role == role).count()
        needed = 5 - current_count
        if needed > 0:
            for _ in range(needed):
                email = f"{role}_{fake.unique.word()}@demo.com"
                user = User(
                    company_id=company.id,
                    email=email,
                    password_hash=get_password_hash(PASSWORD),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    role=role,
                    is_active=True,
                    is_verified=True,
                    phone=fake.phone_number()
                )
                db.add(user)
                users.append(user)
    
    db.commit()
    print(f"Seeded {len(users)} new users.")
    return db.query(User).filter(User.company_id == company.id).all()

def seed_clients(db: Session, company: Company, users: List[User]) -> List[Client]:
    print("Seeding Clients...")
    current_count = db.query(Client).filter(Client.company_id == company.id).count()
    needed = 25 - current_count
    
    new_clients = []
    if needed > 0:
        for _ in range(needed):
            is_corporate = random.choice([True, False])
            # Link to a user if it's a 'client' role user, else None
            client_users = [u for u in users if u.role == 'client']
            linked_user = random.choice(client_users) if client_users and random.random() > 0.7 else None
            
            client = Client(
                company_id=company.id,
                user_id=linked_user.id if linked_user else None,
                client_type='corporate' if is_corporate else 'individual',
                first_name=fake.first_name() if not is_corporate else None,
                last_name=fake.last_name() if not is_corporate else None,
                business_name=fake.company() if is_corporate else None,
                email=linked_user.email if linked_user else fake.email(),
                phone=fake.phone_number(),
                address=fake.address(),
                city=fake.city(),
                status='active',
                risk_profile=random.choice(['low', 'medium', 'high', 'low'])
            )
            db.add(client)
            new_clients.append(client)
            
    db.commit()
    print(f"Seeded {len(new_clients)} new clients.")
    return db.query(Client).filter(Client.company_id == company.id).all()

def seed_policy_types(db: Session, company: Company) -> List[PolicyType]:
    print("Seeding Policy Types...")
    types = [
        {"name": "Auto Insurance", "code": "AUTO"},
        {"name": "Home Insurance", "code": "HOME"},
        {"name": "Health Insurance", "code": "HEALTH"},
        {"name": "Life Insurance", "code": "LIFE"},
        {"name": "Travel Insurance", "code": "TRAVEL"}
    ]
    
    results = []
    for t in types:
        pt = db.query(PolicyType).filter(PolicyType.company_id == company.id, PolicyType.code == t['code']).first()
        if not pt:
            pt = PolicyType(
                company_id=company.id,
                name=t['name'],
                code=t['code'],
                description=fake.sentence(),
                is_active=True
            )
            db.add(pt)
            db.commit()
            db.refresh(pt)
        results.append(pt)
    return results

def seed_policy_services(db: Session, company: Company) -> List[PolicyService]:
    print("Seeding Policy Services...")
    services_data = [
        {
            "name_en": "Courtesy Car",
            "name_fr": "Véhicule de remplacement",
            "default_price": 50.00,
            "description": "Provision of a courtesy car while yours is being repaired."
        },
        {
            "name_en": "Windscreen Cover",
            "name_fr": "Couverture pare-brise",
            "default_price": 25.00,
            "description": "Coverage for windscreen repair or replacement."
        },
        {
            "name_en": "Personal Accident Cover",
            "name_fr": "Couverture accident personnel",
            "default_price": 15.00,
            "description": "Personal accident cover up to £5,000."
        },
        {
            "name_en": "No Claims Discount Protection",
            "name_fr": "Protection du bonus sans sinistre",
            "default_price": 30.00,
            "description": "Protect your No Claims Discount even if you make a claim."
        },
        {
            "name_en": "Breakdown Cover",
            "name_fr": "Assistance routière",
            "default_price": 40.00,
            "description": "Roadside assistance."
        },
        {
            "name_en": "Legal Cover",
            "name_fr": "Protection juridique",
            "default_price": 20.00,
            "description": "Coverage for legal expenses."
        }
    ]

    results = []
    for data in services_data:
        service = db.query(PolicyService).filter(PolicyService.company_id == company.id, PolicyService.name_en == data['name_en']).first()
        if not service:
            service = PolicyService(
                company_id=company.id,
                name_en=data['name_en'],
                name_fr=data['name_fr'],
                default_price=Decimal(data['default_price']),
                description=data['description'],
                is_active=True
            )
            db.add(service)
            db.commit()
            db.refresh(service)
        results.append(service)
    
    print(f"Seeded {len(results)} Policy Services")
    return results

def seed_quotes(db: Session, company: Company, clients: List[Client], policy_types: List[PolicyType], users: List[User]):
    print("Seeding Quotes...")
    current_count = db.query(Quote).filter(Quote.company_id == company.id).count()
    needed = 25 - current_count
    
    if needed > 0:
        for _ in range(needed):
            client = random.choice(clients)
            p_type = random.choice(policy_types)
            creator = random.choice(users)
            
            premium = Decimal(random.randint(50000, 500000))
            
            quote = Quote(
                company_id=company.id,
                client_id=client.id,
                policy_type_id=p_type.id,
                created_by=creator.id,
                quote_number=f"Q-{fake.unique.random_number(digits=8)}",
                coverage_amount=premium * 10,
                premium_amount=premium,
                final_premium=premium,
                status=random.choice(['draft', 'sent', 'accepted', 'rejected', 'expired']),
                valid_until=datetime.now().date() + timedelta(days=30),
                notes=fake.text()
            )
            db.add(quote)
        db.commit()
    print(f"Seeded Quotes (Total now {db.query(Quote).count()})")

def seed_policies(db: Session, company: Company, clients: List[Client], policy_types: List[PolicyType], users: List[User]) -> List[Policy]:
    print("Seeding Policies...")
    current_count = db.query(Policy).filter(Policy.company_id == company.id).count()
    needed = 25 - current_count
    
    if needed > 0:
        for _ in range(needed):
            client = random.choice(clients)
            p_type = random.choice(policy_types)
            creator = random.choice(users)
            
            start_date = fake.date_between(start_date='-1y', end_date='today')
            end_date = start_date + timedelta(days=365)
            premium = Decimal(random.randint(50000, 500000))
            
            policy = Policy(
                company_id=company.id,
                client_id=client.id,
                policy_type_id=p_type.id,
                created_by=creator.id,
                policy_number=f"P-{fake.unique.random_number(digits=8)}",
                coverage_amount=premium * 100,
                premium_amount=premium,
                start_date=start_date,
                end_date=end_date,
                status='active' if end_date > datetime.now().date() else 'expired',
                notes=fake.text()
            )
            db.add(policy)
        db.commit() # Commit to get IDs
    
    print(f"Seeded Policies (Total now {db.query(Policy).count()})")
    return db.query(Policy).filter(Policy.company_id == company.id).all()

def seed_claims(db: Session, company: Company, policies: List[Policy]):
    print("Seeding Claims...")
    current_count = db.query(Claim).filter(Claim.company_id == company.id).count()
    needed = 25 - current_count
    
    if needed > 0:
        for _ in range(needed):
            policy = random.choice(policies)
            
            claim = Claim(
                company_id=company.id,
                policy_id=policy.id,
                client_id=policy.client_id,
                claim_number=f"C-{fake.unique.random_number(digits=8)}",
                incident_date=policy.start_date + timedelta(days=random.randint(1, 100)),
                incident_description=fake.paragraph(),
                incident_location=fake.city(),
                status=random.choice(['submitted', 'under_review', 'approved', 'paid', 'closed']),
                claim_amount=Decimal(random.randint(10000, 1000000))
            )
            db.add(claim)
        db.commit()
    print(f"Seeded Claims (Total now {db.query(Claim).count()})")

def seed_payments(db: Session, company: Company, policies: List[Policy]):
    print("Seeding Payments...")
    current_count = db.query(Payment).filter(Payment.company_id == company.id).count()
    needed = 25 - current_count
    
    if needed > 0:
        for _ in range(needed):
            policy = random.choice(policies)
            
            amount = policy.premium_amount
            
            payment = Payment(
                company_id=company.id,
                policy_id=policy.id,
                client_id=policy.client_id,
                payment_number=f"PAY-{fake.unique.random_number(digits=8)}",
                amount=amount,
                payment_method=random.choice(['mobile_money', 'cash', 'stripe']),
                status='completed',
                paid_at=datetime.utcnow() - timedelta(days=random.randint(0, 60))
            )
            db.add(payment)
        db.commit()
    print(f"Seeded Payments (Total now {db.query(Payment).count()})")
    
def seed_documents(db: Session, company: Company, users: List[User]):
    print("Seeding Documents...")
    current_count = db.query(Document).filter(Document.company_id == company.id).count()
    needed = 25 - current_count
    
    if needed > 0:
        for _ in range(needed):
            uploader = random.choice(users)
            doc = Document(
                company_id=company.id,
                uploaded_by=uploader.id,
                name=f"{fake.word()}_{fake.file_name(extension='pdf')}",
                file_url=f"uploads/dummy_{uuid.uuid4()}.pdf",
                file_type="pdf",
                file_size=random.randint(10000, 5000000),
                label=random.choice(list(DocumentLabel)),
                visibility=random.choice(['PUBLIC', 'PRIVATE']),
                scope=random.choice(['B2B', 'B2C']) if random.random() > 0.5 else None,
                is_shareable=True
            )
            db.add(doc)
        db.commit()
    print(f"Seeded Documents (Total now {db.query(Document).count()})")

def main():
    print("Starting Database Seed...")
    db = SessionLocal()
    try:
        company = seed_company(db)
        admin = seed_admin(db, company)
        users = seed_users(db, company)
        clients = seed_clients(db, company, users)
        p_types = seed_policy_types(db, company)
        services = seed_policy_services(db, company)
        
        seed_quotes(db, company, clients, p_types, users)
        policies = seed_policies(db, company, clients, p_types, users)
        seed_claims(db, company, policies)
        seed_payments(db, company, policies)
        seed_documents(db, company, users)
        
        print("\nDatabase Seeding Complete!")
        print(f"Admin User: {ADMIN_EMAIL}")
        print(f"Password: {PASSWORD}") # Should match what is set in create_admin.py if used previously
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    main()
