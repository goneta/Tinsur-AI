import sqlite3
import os

db_path = 'backend/insurance.db'
table_name = 'client_drivers'

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"Schema for {table_name}:")
cursor.execute(f"PRAGMA table_info({table_name})")
rows = cursor.fetchall()
for r in rows:
    # (id, name, type, notnull, dflt_value, pk)
    print(f"Column: {r[1]}, Type: {r[2]}, NotNull: {r[3]}, Default: {r[4]}, PK: {r[5]}")

conn.close()
