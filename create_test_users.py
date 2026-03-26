import sys
import sqlite3
from datetime import datetime

# Path to database
db_path = "backend/insurance.db"

try:
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("[*] Connected to database:", db_path)
    print()
    
    # Create users table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        first_name TEXT,
        last_name TEXT,
        is_active INTEGER DEFAULT 1,
        is_superuser INTEGER DEFAULT 0,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    print("[OK] Users table ready")
    print()
    
    # Simple password hashing (in real app, use bcrypt)
    import hashlib
    import uuid
    
    def hash_password(password):
        # Simple hash for testing
        return hashlib.sha256(password.encode()).hexdigest()
    
    # Delete old test users
    cursor.execute("DELETE FROM users WHERE email IN (?, ?)", 
                   ("admin@example.com", "client@example.com"))
    
    print("[OK] Cleared old test users")
    print()
    
    # Insert admin user
    admin_id = str(uuid.uuid4())
    admin_pass = hash_password("admin123")
    
    cursor.execute("""
    INSERT INTO users (id, email, password_hash, first_name, last_name, is_active, is_superuser, role)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (admin_id, "admin@example.com", admin_pass, "Admin", "User", 1, 1, "admin"))
    
    print("[OK] Created admin user")
    print("    Email: admin@example.com")
    print("    Password: admin123")
    print("    ID:", admin_id)
    print()
    
    # Insert client user
    client_id = str(uuid.uuid4())
    client_pass = hash_password("client123")
    
    cursor.execute("""
    INSERT INTO users (id, email, password_hash, first_name, last_name, is_active, is_superuser, role)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (client_id, "client@example.com", client_pass, "Test", "Client", 1, 0, "user"))
    
    print("[OK] Created client user")
    print("    Email: client@example.com")
    print("    Password: client123")
    print("    ID:", client_id)
    print()
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print("[OK] Database updated successfully!")
    print()
    print("Now you can login with:")
    print("  Email: admin@example.com")
    print("  Password: admin123")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
