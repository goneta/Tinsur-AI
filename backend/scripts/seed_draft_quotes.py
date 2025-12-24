import uuid
from datetime import datetime, date, timedelta
from app.core.database import SessionLocal
from app.models.company import Company
from app.models.client import Client
from app.models.policy_type import PolicyType
from app.models.quote import Quote
from app.models.user import User

def seed_draft_quotes():
    db = SessionLocal()
    try:
        # 1. Get or create a Company
        company = db.query(Company).first()
        if not company:
            company = Company(
                name="Test Insurance Co",
                email="contact@testins.com",
                phone="123456789"
            )
            db.add(company)
            db.flush()

        # 2. Get or create a User (for creator)
        user = db.query(User).filter(User.email == "admin@example.com").first()
        if not user:
            user = User(
                email="admin@example.com",
                first_name="Admin",
                last_name="User",
                password_hash="dummy_hash",
                role="super_admin",
                is_active=True
            )
            db.add(user)
            db.flush()

        # 3. Get or create a Client
        client = db.query(Client).first()
        if not client:
            client = Client(
                company_id=company.id,
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@example.com",
                phone="555-0199",
                address="456 Oak Ave",
                client_type="individual"
            )
            db.add(client)
            db.flush()

        # 4. Get Policy Types
        pt_auto = db.query(PolicyType).filter(PolicyType.name.ilike("%auto%")).first()
        if not pt_auto:
            pt_auto = PolicyType(name="Automobile", description="Auto Insurance")
            db.add(pt_auto)
            db.flush()
        
        pt_house = db.query(PolicyType).filter(PolicyType.name.ilike("%hous%")).first()
        if not pt_house:
            pt_house = PolicyType(name="Housing", description="Home Insurance")
            db.add(pt_house)
            db.flush()

        # 5. Create Draft Quotes
        quotes_data = [
            ("Q-2025-010", pt_auto.id, "draft", 1200.00, 500000),
            ("Q-2025-011", pt_house.id, "accepted", 2500.00, 1500000),
            ("Q-2025-012", pt_auto.id, "sent", 1100.00, 450000),
            ("Q-2025-013", pt_house.id, "draft", 2200.00, 1200000),
        ]

        for qnum, ptid, status, premium, coverage in quotes_data:
            existing = db.query(Quote).filter(Quote.quote_number == qnum).first()
            if not existing:
                q = Quote(
                    company_id=company.id,
                    client_id=client.id,
                    policy_type_id=ptid,
                    quote_number=qnum,
                    coverage_amount=coverage,
                    premium_amount=premium,
                    final_premium=premium,
                    status=status,
                    valid_until=(date.today() + timedelta(days=30)),
                    created_by=user.id
                )
                db.add(q)
        
        db.commit()
        print("Successfully seeded draft quotes.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding quotes: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_draft_quotes()
