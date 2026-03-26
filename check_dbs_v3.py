import sqlite3
import os

dbs = ['insurance.db', 'backend/insurance.db', 'backend/app/insurance.db']
tables = ['users', 'clients', 'quotes', 'policies', 'premium_policies', 'premium_policy_types', 'translations']

for db_path in dbs:
    full_path = os.path.join(os.getcwd(), db_path)
    print(f"\n--- Database: {db_path} ---")
    if not os.path.exists(full_path):
        print("File does not exist.")
        continue
    
    try:
        conn = sqlite3.connect(full_path)
        cursor = conn.cursor()
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table}: {count}")
            except sqlite3.OperationalError:
                print(f"{table}: Table not found")
        conn.close()
    except Exception as e:
        print(f"Error accessing DB: {e}")
