import sqlite3
import os

db_path = 'backend/insurance.db'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT count(*) FROM client_automobile")
    count = cursor.fetchone()[0]
    print(f"Total vehicles: {count}")
    
    cursor.execute("SELECT vehicle_make, vehicle_model, vehicle_registration FROM client_automobile LIMIT 5")
    rows = cursor.fetchall()
    print("First 5 vehicles:")
    for row in rows:
        print(row)
finally:
    conn.close()
