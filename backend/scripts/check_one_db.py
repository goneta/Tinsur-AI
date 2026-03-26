import sqlite3
import os

path = 'backend/app/insurance.db'
print(f"Checking {path}...")
conn = sqlite3.connect(path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cursor.fetchall()]
print(f"Tables: {tables}")
if 'translations' in tables:
    print("Found translations table!")
    cursor.execute("SELECT key, language_code, value FROM translations WHERE key LIKE 'service.%' LIMIT 20")
    for r in cursor.fetchall():
        print(r)
else:
    print("Translations NOT FOUND")
conn.close()
