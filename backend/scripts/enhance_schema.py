import sqlite3
import os

def enhance_schema():
    db_path = "insurance.db"
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("Enhancing schema...")
        
        # PremiumPolicyType
        try:
            cursor.execute("ALTER TABLE premium_policy_types ADD COLUMN tagline VARCHAR(255)")
        except sqlite3.OperationalError:
            print("  Column tagline already exists in premium_policy_types")
            
        try:
            cursor.execute("ALTER TABLE premium_policy_types ADD COLUMN is_featured BOOLEAN DEFAULT 0")
        except sqlite3.OperationalError:
            print("  Column is_featured already exists in premium_policy_types")

        # Quote
        try:
            cursor.execute("ALTER TABLE quotes ADD COLUMN valid_for_days INTEGER DEFAULT 30")
        except sqlite3.OperationalError:
            print("  Column valid_for_days already exists in quotes")

        # Policy
        try:
            cursor.execute("ALTER TABLE policies ADD COLUMN auto_renew BOOLEAN DEFAULT 0")
        except sqlite3.OperationalError:
            print("  Column auto_renew already exists in policies")

        # PolicyService
        try:
            cursor.execute("ALTER TABLE policy_services ADD COLUMN category VARCHAR(100) DEFAULT 'Other'")
        except sqlite3.OperationalError:
            print("  Column category already exists in policy_services")
            
        try:
            cursor.execute("ALTER TABLE policy_services ADD COLUMN icon_name VARCHAR(50) DEFAULT 'Shield'")
        except sqlite3.OperationalError:
            print("  Column icon_name already exists in policy_services")

        conn.commit()
        print("Schema enhanced successfully!")

    except Exception as e:
        print(f"Error enhancing schema: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    enhance_schema()
