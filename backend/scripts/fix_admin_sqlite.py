import sqlite3
import os
import sys
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def fix_admin_sqlite():
    # Force backend path
    db_path = os.path.join(os.getcwd(), 'backend', 'insurance.db')
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    print(f"Connecting to SQLite DB: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        email = "admin@demoinsurance.com"
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        
        new_hash = get_password_hash("admin123")
        
        if row:
            print(f"User found (ID: {row[0]}). Updating password...")
            cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_hash, email))
            if cursor.rowcount > 0:
                print("✓ Password updated.")
            else:
                print("No rows updated (strange).")
        else:
            print("User not found via sqlite3 query.")
            
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_admin_sqlite()
