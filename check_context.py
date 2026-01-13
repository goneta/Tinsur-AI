import sqlite3
import os

db_path = 'backend/insurance.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("--- Companies ---")
    cursor.execute("SELECT id, name, subdomain FROM companies")
    for row in cursor.fetchall():
        print(row)
        
    print("\n--- Admin User ---")
    cursor.execute("SELECT id, email, company_id, role FROM users WHERE email='admin@demoinsurance.com'")
    for row in cursor.fetchall():
        print(row)
        
    print("\n--- Client Counts per Company ---")
    cursor.execute("SELECT company_id, count(*) FROM clients GROUP BY company_id")
    for row in cursor.fetchall():
        print(row)
        
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
