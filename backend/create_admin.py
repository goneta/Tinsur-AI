import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from sqlalchemy import text
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.company import Company
from app.core.security import get_password_hash
# Import all models so Base.metadata knows about every table
import app.models  # noqa: F401


def ensure_schema():
    """Add any missing columns to the companies table so queries work."""
    # Columns the model expects: (column_name, SQL type + default)
    expected_columns = {
        "subdomain": "VARCHAR(100) UNIQUE",
        "email": "VARCHAR(255)",
        "phone": "VARCHAR(50)",
        "address": "TEXT",
        "registration_number": "VARCHAR(100)",
        "system_registration_number": "VARCHAR(50)",
        "bank_details": "JSON",
        "mobile_money_accounts": "JSON",
        "apr_percent": "FLOAT DEFAULT 0.0",
        "arrangement_fee": "NUMERIC(15,2) DEFAULT 0.0",
        "extra_fee": "NUMERIC(15,2) DEFAULT 0.0",
        "currency": "VARCHAR(10) DEFAULT 'USD'",
        "country": "VARCHAR(100)",
        "timezone": "VARCHAR(50) DEFAULT 'UTC'",
        "government_tax_percent": "FLOAT DEFAULT 0.0",
        "admin_fee": "NUMERIC(15,2) DEFAULT 0.0",
        "admin_fee_percent": "FLOAT DEFAULT 0.0",
        "admin_discount_percent": "FLOAT DEFAULT 0.0",
        "is_active": "BOOLEAN DEFAULT TRUE",
        "logo_url": "VARCHAR",
        "primary_color": "VARCHAR(10)",
        "secondary_color": "VARCHAR(10)",
        "theme_colors": "VARCHAR",
        "features": "JSON",
        "ai_plan": "VARCHAR(20) DEFAULT 'CREDIT'",
        "ai_api_key_encrypted": "VARCHAR(500)",
        "ai_credits_balance": "FLOAT DEFAULT 100.0",
        "created_at": "TIMESTAMP WITHOUT TIME ZONE",
        "updated_at": "TIMESTAMP WITHOUT TIME ZONE",
    }

    with engine.connect() as conn:
        # Get existing columns
        result = conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='companies'"
        ))
        existing = {row[0] for row in result}

        added = []
        for col_name, col_type in expected_columns.items():
            if col_name not in existing:
                conn.execute(text(
                    f"ALTER TABLE companies ADD COLUMN {col_name} {col_type}"
                ))
                added.append(col_name)

        if added:
            # Back-fill subdomain for any existing rows
            if "subdomain" in added:
                conn.execute(text(
                    "UPDATE companies SET subdomain = LOWER(REPLACE(name, ' ', '-')) "
                    "WHERE subdomain IS NULL"
                ))
            conn.commit()
            print(f"+ Added {len(added)} missing column(s) to companies: {', '.join(added)}")


def create_admin():
    # Bring the DB schema up to date
    ensure_schema()
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if admin exists
        admin_email = "admin@demoinsurance.com"
        admin = db.query(User).filter(User.email == admin_email).first()

        if admin:
            print(f"Admin user already exists: {admin_email}")
            print(f"Updating password to 'Admin123!'...")
            admin.password_hash = get_password_hash("Admin123!")
            db.commit()
            print("+ Password updated successfully!")
        else:
            print(f"Creating admin user: {admin_email}")

            # Ensure company exists
            company = db.query(Company).filter(Company.name == "Demo Insurance Co").first()
            if not company:
                company = Company(
                    name="Demo Insurance Co",
                    subdomain="demo-insurance",
                    email="info@demoinsurance.com",
                    is_active=True,
                )
                db.add(company)
                db.commit()
                db.refresh(company)
                print("+ Created Demo Insurance Co")

            # Create admin user
            admin = User(
                email=admin_email,
                password_hash=get_password_hash("Admin123!"),
                first_name="Admin",
                last_name="User",
                user_type="super_admin",
                company_id=company.id,
                is_active=True,
                is_verified=True,
            )
            db.add(admin)
            db.commit()
            print("+ Admin user created successfully!")

        print("\n" + "=" * 50)
        print("Admin Login Credentials:")
        print("=" * 50)
        print(f"Email: {admin_email}")
        print(f"Password: Admin123!")
        print("=" * 50)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
