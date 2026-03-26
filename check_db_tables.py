import sqlite3
import os

db_path = "backend/insurance.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('client_automobile', 'client_drivers');")
tables = cursor.fetchall()
print("Found tables:", [t[0] for t in tables])
conn.close()
