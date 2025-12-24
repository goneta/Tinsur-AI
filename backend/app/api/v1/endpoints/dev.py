from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.company import Company
from app.models.user import User
from app.core.security import get_password_hash

router = APIRouter()

@router.post("/hash")
def test_hash(password: str = "test"):
    return {"hash": get_password_hash(password)}

@router.post("/seed")
def seed_data(db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.email == "contact@demoinsurance.com").first()
    if not company:
        # Create Company
        company = Company(
            name="Demo Insurance Company",
            subdomain="demo",
            email="contact@demoinsurance.com",
            is_active=True
        )
        db.add(company)
        db.commit()
        db.refresh(company)
    
    # Check if admin exists
    admin = db.query(User).filter(User.email == "admin@demoinsurance.com").first()
    if not admin:
        # Create Admin
        admin = User(
            company_id=company.id,
            email="admin@demoinsurance.com",
            password_hash=get_password_hash("Admin123!"),
            first_name="Super",
            last_name="Admin",
            role="super_admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        return {"message": "Admin user created", "user": "admin@demoinsurance.com"}
    
    return {"message": "Data already seeded (Admin exists)", "user": "admin@demoinsurance.com"}

@router.post("/seed-ai-test-users")
def seed_ai_test_users(db: Session = Depends(get_db)):
    """Creates test users for different AI plan tiers."""
    company = db.query(Company).filter(Company.subdomain == "demo").first()
    if not company:
        company = Company(
            name="AI Test Corp",
            subdomain="demo",
            email="ai-test@demo.com",
            is_active=True,
            ai_plan="BASIC"
        )
        db.add(company)
        db.commit()
        db.refresh(company)

    plans = [
        ("ai_basic@demo.com", "BASIC", 0.0),
        ("ai_byok@demo.com", "BYOK", 0.0),
        ("ai_credit_full@demo.com", "CREDIT", 50.0),
        ("ai_credit_empty@demo.com", "CREDIT", 0.0),
    ]

    created = []
    for email, plan, balance in plans:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Create a separate company per user to test isolation easily
            test_company = Company(
                name=f"AI {plan} Corp",
                subdomain=email.split("@")[0].replace("_", "-"),
                email=f"corp-{email}",
                ai_plan=plan,
                ai_credits_balance=balance,
                is_active=True
            )
            db.add(test_company)
            db.commit()
            db.refresh(test_company)

            user = User(
                company_id=test_company.id,
                email=email,
                password_hash=get_password_hash("Test123!"),
                first_name="AI",
                last_name=plan,
                role="company_admin",
                is_active=True
            )
            db.add(user)
            db.commit()
            created.append(email)

    return {"message": "AI test users seeded", "created": created}

@router.post("/topup-dev")
def topup_credits_dev(amount: float, company_id: str, db: Session = Depends(get_db)):
    """Directly adds credits for testing."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company.ai_credits_balance = (company.ai_credits_balance or 0.0) + amount
    db.commit()
    return {"message": f"Topped up {amount}", "new_balance": company.ai_credits_balance}
