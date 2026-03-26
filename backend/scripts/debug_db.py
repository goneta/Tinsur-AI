import sqlite3
import os

db_paths = [
    'c:/Users/user/Desktop/Tinsur.AI/insurance.db',
    'c:/Users/user/Desktop/Tinsur.AI/backend/insurance.db',
    'c:/Users/user/Desktop/Tinsur.AI/backend/app/insurance.db'
]

for db_path in db_paths:
    if not os.path.exists(db_path):
        print(f"NOT FOUND: {db_path}")
        continue
        
    print(f"\nChecking DB: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print("Tables found:", tables)
        
        if 'translations' in tables:
            print("Table 'translations' found.")
            cursor.execute("SELECT COUNT(*) FROM translations")
            print("Row count in translations:", cursor.fetchone()[0])
            cursor.execute("SELECT key, language_code, value FROM translations WHERE key LIKE 'service.%' LIMIT 5")
            for row in cursor.fetchall():
                print(row)
        else:
            print("Table 'translations' NOT found!")
            
        conn.close()
    except Exception as e:
        print(f"Error checking {db_path}: {e}")
