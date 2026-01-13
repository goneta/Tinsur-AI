import sqlite3
import os

db_path = 'backend/insurance.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT count(*) FROM translations")
    print(f"Total translations: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT language_code, key, value FROM translations WHERE key LIKE 'quote.wizard.%' LIMIT 20")
    rows = cursor.fetchall()
    print("\nSample quote.wizard translations:")
    for row in rows:
        print(f"{row[0]} | {row[1]} = {row[2]}")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
