import random
import uuid
import string
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.company import Company
from app.models.client import Client
from app.models.policy import Policy
from app.models.quote import Quote
from app.models.claim import Claim
from app.models.payment import Payment
from app.models.policy_type import PolicyType
from app.core.security import get_password_hash

# Helper for random strings
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def random_phone():
    return f"+225 {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}"

NAMES = ["Jean", "Marie", "Koffi", "Awa", "Moussa", "Fatou", "Yao", "Konan", "Adama", "Bintou"]
LAST_NAMES = ["Kouadio", "Koné", "Traoré", "Ouattara", "Coulibaly", "Bakayoko", "Diabaté", "Sidibé", "Diallo", "Soro"]
COMPANY_SUFFIXES = ["Assurances", "S.A.", "SARL", "Groupe", "Solutions"]
JOBS = ["Ingénieur", "Enseignant", "Médecin", "Artiste", "Commerçant", "Chauffeur", "Informaticien"]
ADDRESSES = ["Plateau, Rue du Commerce", "Cocody, Riviéra 3", "Marcory, Zone 4", "Adjamé, 220 Logements", "Yopougon, Selmer"]

POLICY_TYPES_DATA = [
    {"name": "Automobile", "code": "AUTO", "description": "Assurance véhicule motorisé"},
    {"name": "Habitation", "code": "HOME", "description": "Protection de votre domicile"},
    {"name": "Santé", "code": "HEALTH", "description": "Couverture médicale complète"},
    {"name": "Vie", "code": "LIFE", "description": "Assurance prévoyance et décès"}
]

def seed_data():
    db = SessionLocal()
    try:
        print("Starting database seeding...")
        
        # 0. Create default company and admin
        admin_email = "admin@demoinsurance.com"
        company = db.query(Company).filter(Company.subdomain == "demoinsurance.com").first()
        if not company:
            company = Company(
                name="Demo Insurance Co", 
                subdomain="demoinsurance.com", 
                email="contact@demoinsurance.com",
                is_active=True,
                currency="XOF",
                country="Côte d'Ivoire"
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            print("Default company created.")
        
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                password_hash=get_password_hash("admin123"),
                first_name="Admin",
                last_name="User",
                role="super_admin",
                company_id=company.id,
                is_active=True,
                is_verified=True
            )
            db.add(admin)
            db.commit()
            print(f"Admin created: {admin_email}")

        # 1. Create Policy Types for the company
        policy_types = []
        for pt_data in POLICY_TYPES_DATA:
            pt = db.query(PolicyType).filter(PolicyType.company_id == company.id, PolicyType.code == pt_data["code"]).first()
            if not pt:
                pt = PolicyType(
                    company_id=company.id,
                    name=pt_data["name"],
                    code=pt_data["code"],
                    description=pt_data["description"]
                )
                db.add(pt)
                policy_types.append(pt)
            else:
                policy_types.append(pt)
        db.commit()
        for pt in policy_types:
            db.refresh(pt)

        # 2. Create Agents (5)
        agents = []
        for i in range(5):
            fname = random.choice(NAMES)
            lname = random.choice(LAST_NAMES)
            email = f"{fname.lower()}.{lname.lower()}{i}@demo.com"
            agent = db.query(User).filter(User.email == email).first()
            if not agent:
                agent = User(
                    email=email,
                    password_hash=get_password_hash("password123"),
                    first_name=fname,
                    last_name=lname,
                    phone=random_phone(),
                    role="agent",
                    company_id=company.id,
                    is_active=True,
                    is_verified=True
                )
                db.add(agent)
                agents.append(agent)
            else:
                agents.append(agent)
        db.commit()
        for a in agents:
            db.refresh(a)
        print(f"Ensured {len(agents)} agents.")

        # 3. Create Clients (10)
        clients = []
        for i in range(10):
            fname = random.choice(NAMES)
            lname = random.choice(LAST_NAMES)
            email = f"{fname.lower()}.{lname.lower()}{i}@client.com"
            
            # Create User first for client portal access
            user_client = db.query(User).filter(User.email == email).first()
            if not user_client:
                user_client = User(
                    email=email,
                    password_hash=get_password_hash("password123"),
                    first_name=fname,
                    last_name=lname,
                    phone=random_phone(),
                    role="client",
                    company_id=company.id,
                    is_active=True,
                    is_verified=True
                )
                db.add(user_client)
                db.commit()
                db.refresh(user_client)
            
            # Create Client profile
            client_profile = db.query(Client).filter(Client.user_id == user_client.id).first()
            if not client_profile:
                client_profile = Client(
                    company_id=company.id,
                    user_id=user_client.id,
                    client_type="individual",
                    first_name=fname,
                    last_name=lname,
                    email=email,
                    phone=user_client.phone,
                    date_of_birth=date.today() - timedelta(days=random.randint(18*365, 60*365)),
                    address=random.choice(ADDRESSES),
                    occupation=random.choice(JOBS),
                    annual_income=random.randint(500000, 5000000),
                    status="active"
                )
                db.add(client_profile)
                clients.append(client_profile)
            else:
                clients.append(client_profile)
        db.commit()
        for c in clients:
            db.refresh(c)
        print(f"Ensured {len(clients)} client profiles.")

        # 4. Create Policies, Quotes, Claims
        for client in clients:
            # Each client gets 1-2 quotes/policies
            for _ in range(random.randint(1, 2)):
                pt = random.choice(policy_types)
                premium = round(random.uniform(50000, 500000), 0)
                
                # Create Quote
                quote_num = f"QUO-{random.randint(1000,9999)}-{random_string(4).upper()}"
                status = random.choice(["draft", "sent", "accepted", "converted"])
                quote = Quote(
                    company_id=company.id,
                    client_id=client.id,
                    policy_type_id=pt.id,
                    quote_number=quote_num,
                    coverage_amount=premium * 10,
                    premium_amount=premium,
                    final_premium=premium,
                    status=status,
                    created_by=admin.id,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
                )
                db.add(quote)
                db.commit()
                db.refresh(quote)
                
                # If converted, create policy
                if status == "converted":
                    pol_num = f"POL-{random.randint(1000,9999)}-{random_string(4).upper()}"
                    start_date = date.today() - timedelta(days=random.randint(0, 30))
                    policy = Policy(
                        company_id=company.id,
                        client_id=client.id,
                        policy_type_id=pt.id,
                        quote_id=quote.id,
                        policy_number=pol_num,
                        premium_amount=premium,
                        coverage_amount=premium * 10,
                        start_date=start_date,
                        end_date=start_date + timedelta(days=365),
                        status="active",
                        created_by=admin.id,
                        created_at=datetime.combine(start_date, datetime.min.time())
                    )
                    db.add(policy)
                    db.commit()
                    db.refresh(policy)
                    
                    # Random claim
                    if random.random() < 0.2:
                        claim_num = f"CLM-{random.randint(1000,9999)}-{random_string(4).upper()}"
                        claim = Claim(
                            company_id=company.id,
                            policy_id=policy.id,
                            client_id=client.id,
                            claim_number=claim_num,
                            claim_amount=round(premium * random.uniform(0.1, 0.5), 0),
                            status=random.choice(["submitted", "in_review", "approved"]),
                            incident_date=date.today() - timedelta(days=random.randint(1, 15)),
                            description="Accident mineur ou dommage matériel."
                        )
                        db.add(claim)
                    
                    # One payment
                    pay_num = f"PAY-{random.randint(1000,9999)}-{random_string(4).upper()}"
                    payment = Payment(
                        company_id=company.id,
                        policy_id=policy.id,
                        client_id=client.id,
                        payment_number=pay_num,
                        amount=premium / 12,
                        status="completed",
                        payment_method="orange_money",
                        paid_at=datetime.utcnow() - timedelta(days=random.randint(1, 10))
                    )
                    db.add(payment)

        db.commit()
        print("Database seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
