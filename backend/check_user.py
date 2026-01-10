import sqlite3
import os

db_path = 'insurance.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

email = 'admin@demoinsurance.com'
cursor.execute("SELECT id, email, role, is_active, is_verified FROM users WHERE email = ?", (email,))
user = cursor.fetchone()

if user:
    print(f"User Found: ID={user[0]}, Email={user[1]}, Role={user[2]}, Active={user[3]}, Verified={user[4]}")
else:
    print(f"User {email} NOT found in database.")
    # List all users to see what's there
    cursor.execute("SELECT email, role FROM users LIMIT 10")
    users = cursor.fetchall()
    print("Available users:", users)

conn.close()
