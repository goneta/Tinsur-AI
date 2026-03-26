import logging
import random
import uuid
from datetime import datetime, date, timedelta
from app.core.database import SessionLocal
from app.models.company import Company
from app.models.client import Client
from app.models.premium_policy import PremiumPolicyType
from app.models.quote import Quote
from app.models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_robust_quotes():
    db = SessionLocal()
    try:
        logger.info("Starting robust quote seeding...")

        # 1. Get or create a Company
        company = db.query(Company).first()
        if not company:
            company = Company(
                name="Tinsur AI Demo Co",
                email="contact@tinsur.ai",
                phone="123456789"
            )
            db.add(company)
            db.flush()
        logger.info(f"Using Company: {company.name}")

        # 2. Get or create a User (Creator)
        user = db.query(User).filter(User.email == "admin@demoinsurance.com").first()
        if not user:
            # Fallback to any user if admin doesn't exist
            user = db.query(User).first()
            
        if not user:
            # Create if absolutely no users
            user = User(
                email="admin@demoinsurance.com",
                company_id=company.id,
                first_name="Admin",
                last_name="User",
                password_hash="$2b$12$K.XyV.h9/8/g/f.k/j.l/e.a.b.c.d.e.f.g.h", # dummy hash
                role="super_admin",
                is_active=True
            )
            db.add(user)
            db.flush()
        logger.info(f"Using Creator: {user.email}")

        # 3. Create Multiple Clients
        first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
        last_names = ["Doe", "Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore"]
        clients = []
        
        existing_client_count = db.query(Client).count()
        if existing_client_count < 10:
            for i in range(10):
                fn = random.choice(first_names)
                ln = random.choice(last_names)
                client = Client(
                    company_id=company.id,
                    first_name=fn,
                    last_name=ln,
                    email=f"{fn.lower()}.{ln.lower()}{i}@example.com",
                    phone=f"555-01{i:02d}",
                    address=f"{random.randint(100, 999)} Main St",
                    client_type=random.choice(["individual", "business"])
                )
                db.add(client)
                clients.append(client)
            db.flush()
            logger.info(f"Created {len(clients)} new clients.")
        else:
            clients = db.query(Client).limit(20).all()
            logger.info("Using existing clients.")

        # 4. Create Premium Policy Types
        policy_types = []
        pt_names = ["Gold Driver", "Silver Commuter", "Bronze Basic", "Platinum Executive"]
        
        for name in pt_names:
            pt = db.query(PremiumPolicyType).filter(PremiumPolicyType.name == name).first()
            if not pt:
                pt = PremiumPolicyType(
                    company_id=company.id,
                    name=name,
                    description=f"Comprehensive coverage for {name}",
                    price=random.randint(500, 2000),
                    excess=random.randint(100, 500),
                    is_active=True
                )
                db.add(pt)
                db.flush()
            policy_types.append(pt)
        logger.info(f"Ensured {len(policy_types)} policy types exist.")

        # 5. Create Quotes (Mix of statuses)
        statuses = ['draft', 'sent', 'accepted', 'rejected', 'expired']
        
        # We want to add 5 fresh quotes every time this is run
        created_count = 0
        current_year = date.today().year
        
        for i in range(1, 6):
            # Use timestamp to ensure uniqueness
            timestamp_suffix = int(datetime.now().timestamp())
            q_num = f"Q-{current_year}-{timestamp_suffix}-{i}"
            
            # Check if exists (unlikely now)
            if db.query(Quote).filter(Quote.quote_number == q_num).first():
                continue

            cli = random.choice(clients)
            pt = random.choice(policy_types)
            status = random.choice(statuses)
            
            # Vary dates
            created_days_ago = random.randint(0, 60)
            created_at = datetime.now() - timedelta(days=created_days_ago)
            valid_until = created_at.date() + timedelta(days=30)
            
            base_premium = float(pt.price)
            risk_factor = random.uniform(0.8, 1.5)
            final_premium = base_premium * risk_factor

            q = Quote(
                company_id=company.id,
                client_id=cli.id,
                policy_type_id=pt.id,
                quote_number=q_num,
                coverage_amount=random.choice([500000, 1000000, 2000000]),
                premium_amount=final_premium,
                final_premium=final_premium,
                tax_amount=final_premium * 0.18, # 18% tax example
                status=status,
                valid_until=valid_until,
                premium_frequency=random.choice(['annual', 'monthly']),
                created_by=user.id,
                created_at=created_at,
                updated_at=created_at,
                notes=f"Auto-generated quote for {cli.display_name}"
            )
            db.add(q)
            created_count += 1
        
        db.commit()
        logger.info(f"Successfully created {created_count} new quotes.")
        logger.info("Seed Robust Quotes Completed Successfully.")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding quotes: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_robust_quotes()
