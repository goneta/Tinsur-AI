import sqlite3
import os

db_paths = ["backend/insurance.db", "insurance.db", "backend/app/insurance.db"]

def migrate():
    for db_path in db_paths:
        if not os.path.exists(db_path):
            print(f"Database {db_path} not found. Skipping...")
            continue
        
        print(f"Migrating {db_path}...")
        conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Add columns to companies
    try:
        cursor.execute("ALTER TABLE companies ADD COLUMN admin_fee_percent FLOAT DEFAULT 0.0")
        print("Added admin_fee_percent to companies")
    except sqlite3.OperationalError as e:
        print(f"Error adding admin_fee_percent to companies: {e}")

    try:
        cursor.execute("ALTER TABLE companies ADD COLUMN admin_discount_percent FLOAT DEFAULT 0.0")
        print("Added admin_discount_percent to companies")
    except sqlite3.OperationalError as e:
        print(f"Error adding admin_discount_percent to companies: {e}")

    # Add columns to quotes
    try:
        cursor.execute("ALTER TABLE quotes ADD COLUMN admin_fee_percent FLOAT DEFAULT 0.0")
        print("Added admin_fee_percent to quotes")
    except sqlite3.OperationalError as e:
        print(f"Error adding admin_fee_percent to quotes: {e}")

    try:
        cursor.execute("ALTER TABLE quotes ADD COLUMN admin_discount_percent FLOAT DEFAULT 0.0")
        print("Added admin_discount_percent to quotes")
    except sqlite3.OperationalError as e:
        print(f"Error adding admin_discount_percent to quotes: {e}")

    try:
        cursor.execute("ALTER TABLE quotes ADD COLUMN calculation_breakdown JSON DEFAULT '{}'")
        print("Added calculation_breakdown to quotes")
    except sqlite3.OperationalError as e:
        print(f"Error adding calculation_breakdown to quotes: {e}")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
