
import sys
import os
from sqlalchemy import text

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.database import engine, Base
from app.models import user, company, policy, quote, endorsement, underwriting, regulatory, archive

def fix_schema():
    print("Starting manual schema update...")
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        # 1. Update Users Table
        try:
            print("Updating users table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS underwriting_limit NUMERIC(15, 2) DEFAULT 0.00"))
        except Exception as e:
            print(f"Error updating users: {e}")

        # 2. Update Policies Table
        try:
            print("Updating policies table...")
            conn.execute(text("ALTER TABLE policies ADD COLUMN IF NOT EXISTS ifrs17_group_id UUID REFERENCES ifrs17_groups(id)"))
        except Exception as e:
            print(f"Error updating policies (might fail if ifrs17_groups doesn't exist yet): {e}")

        # 3. Create New Tables (IFRS17Group, RegulatoryMetricSnapshot, PolicyArchive, etc.)
        # Base.metadata.create_all will only create missing tables
        print("Creating missing tables...")
        Base.metadata.create_all(bind=engine)
        
        # Retry Policies update if it failed before due to missing FK target
        try:
            print("Retrying policies table update for FK...")
            conn.execute(text("ALTER TABLE policies ADD COLUMN IF NOT EXISTS ifrs17_group_id UUID REFERENCES ifrs17_groups(id)"))
        except Exception as e:
             print(f"Error updating policies (retry): {e}")

        # 4. Update Underwriting Referrals (if it exists)
        try:
            print("Updating underwriting_referrals table...")
            # Check if endorsement_id exists
            conn.execute(text("ALTER TABLE underwriting_referrals ADD COLUMN IF NOT EXISTS endorsement_id UUID REFERENCES endorsements(id) ON DELETE CASCADE"))
            
            # Make quote_id nullable
            conn.execute(text("ALTER TABLE underwriting_referrals ALTER COLUMN quote_id DROP NOT NULL"))
            
            # Add Unique Constraints if needed (handled by index usually)
        except Exception as e:
            print(f"Error updating underwriting_referrals: {e}")

    print("Schema update completed.")

if __name__ == "__main__":
    fix_schema()
