import sqlite3
import os

db_path = 'backend/insurance.db'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT id, first_name, last_name, date_of_birth, risk_profile FROM clients LIMIT 5")
    rows = cursor.fetchall()
    print("First 5 clients:")
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]} {row[2]}")
finally:
    conn.close()
