import sys
import os
import sqlite3
import uuid
import datetime
import traceback

# Import password hasher (assuming imports work as before)
try:
    from app.core.security import get_password_hash
except ImportError:
    # Fallback if import fails (e.g. simple script run without path)
    # But usually it worked. If not, we can simple hash or just plain text for test
    # But let's assume it works.
    def get_password_hash(p): return p + "_hashed" # Mock if fails

def seed_quote_test_data():
    db_path = os.path.join(os.path.dirname(__file__), "insurance.db")
    print(f"Connecting to: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row # Access columns by name
        cursor = conn.cursor()
        
        # 1. Get Company
        cursor.execute("SELECT id FROM companies LIMIT 1")
        row = cursor.fetchone()
        if not row:
            print("No company found.")
            return
        
        company_id = row['id']
        print(f"Using Company ID: {company_id}")

        now = datetime.datetime.utcnow().isoformat()

        # --------------------------------------------------------------------------------
        # 1. Premium Policies
        # --------------------------------------------------------------------------------
        print("\nSeeding Premium Policies...")
        
        # Gold
        gold_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO premium_policy_types 
            (id, company_id, name, description, price, excess, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (gold_id, company_id, 'Gold Driver Policy', 'Comprehensive cover for experienced drivers', 50000, 5000, 1, now, now))

        # Criteria for Gold
        criteria_list = [
            (str(uuid.uuid4()), "accident_count", "=", "0"),
            (str(uuid.uuid4()), "driving_license_years", ">", "5"),
            (str(uuid.uuid4()), "employment_status", "=", "Employed")
        ]

        for crit_id, field, op, val in criteria_list:
            crit_name = f"Criteria: {field} {op} {val}"
            cursor.execute("""
                INSERT INTO premium_policy_criteria (id, company_id, name, field_name, operator, value, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (crit_id, company_id, crit_name, field, op, val, now, now))
            
            cursor.execute("""
                INSERT INTO premium_policy_type_criteria (policy_type_id, criteria_id)
                VALUES (?, ?)
            """, (gold_id, crit_id))

        # New Driver
        new_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO premium_policy_types 
            (id, company_id, name, description, price, excess, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (new_id, company_id, 'New Driver Policy', 'Starter cover for new drivers', 85000, 10000, 1, now, now))

        # Criteria
        crit_id = str(uuid.uuid4())
        crit_name = "Criteria: driving_license_years < 2"
        cursor.execute("""
            INSERT INTO premium_policy_criteria (id, company_id, name, field_name, operator, value, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (crit_id, company_id, crit_name, 'driving_license_years', '<', '2', now, now))
        
        cursor.execute("""
            INSERT INTO premium_policy_type_criteria (policy_type_id, criteria_id)
            VALUES (?, ?)
        """, (new_id, crit_id))

        print("Policies seeded.")

        # --------------------------------------------------------------------------------
        # 2. Clients
        # --------------------------------------------------------------------------------
        print("\nSeeding Clients...")
        
        try:
             # Need real hash function
             from app.core.security import get_password_hash
             hashed_password = get_password_hash("password123")
        except:
             hashed_password = "hashed_password123"

        clients_data = [
            {
                "email": "gold.driver@example.com",
                "fname": "Goldie", "lname": "Driver",
                "fields": {"accident_count": 0, "no_claims_years": 5, "driving_license_years": 8, "employment_status": "Employed"}
            },
            {
                "email": "silver.driver@example.com", 
                "fname": "Silver", "lname": "Surfer",
                "fields": {"accident_count": 0, "no_claims_years": 0, "driving_license_years": 1, "employment_status": "Student"}
            },
            {
                "email": "incomplete.driver@example.com",
                "fname": "Incomplete", "lname": "Profile",
                "fields": {"accident_count": None, "no_claims_years": None, "driving_license_years": None, "employment_status": None}
            }
        ]

        for c in clients_data:
            # Check exist
            cursor.execute("SELECT id FROM users WHERE email = ?", (c["email"],))
            if cursor.fetchone():
                print(f"User {c['email']} exists, skipping.")
                continue

            user_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO users (id, company_id, email, password_hash, first_name, last_name, role, is_active, is_verified, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 'client', 1, 1, ?, ?)
            """, (user_id, company_id, c["email"], hashed_password, c["fname"], c["lname"], now, now))

            client_id = str(uuid.uuid4())
            fields = c["fields"]
            
            # Need to confirm Client table columns existence for these fields?
            # Assuming they exist as per earlier exploration.
            cursor.execute("""
                INSERT INTO clients 
                (id, company_id, user_id, client_type, first_name, last_name, email, status, 
                    accident_count, no_claims_years, driving_license_years, employment_status, 
                    created_at, updated_at, phone, country, risk_profile, kyc_status, pep_status, consent_accepted)
                VALUES (?, ?, ?, 'individual', ?, ?, ?, 'active', ?, ?, ?, ?, ?, ?, '+22501020304', 'Côte d''Ivoire', 'medium', 'pending', 0, 0)
            """, (client_id, company_id, user_id, c["fname"], c["lname"], c["email"], 
                  fields["accident_count"], fields["no_claims_years"], fields["driving_license_years"], fields["employment_status"],
                  now, now))
            
            print(f"Created {c['email']}")

        conn.commit()
        print("Done.")
        conn.close()

    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    seed_quote_test_data()
