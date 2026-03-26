import sys
import sqlite3
import uuid
from datetime import datetime

sys.path.insert(0, "backend")
from app.core.security import get_password_hash

db_path = "backend/insurance.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("[*] Updating users table with all required columns...")
    
    # Delete old test users
    cursor.execute("DELETE FROM users WHERE email IN (?, ?)", 
                   ("admin@example.com", "client@example.com"))
    
    # Create admin user with ALL required fields
    admin_id = str(uuid.uuid4())
    admin_hash = get_password_hash("admin123")
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
    INSERT INTO users (id, email, password_hash, first_name, last_name, user_type, 
                      is_active, is_verified, compliance_status, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (admin_id, "admin@example.com", admin_hash, "Admin", "User", "super_admin",
          1, 1, "approved", now, now))
    
    print("[OK] Admin user created")
    print(f"    ID: {admin_id}")
    print("    Email: admin@example.com")
    print("    Password: admin123")
    print("    Type: super_admin")
    print()
    
    # Create client user with ALL required fields
    client_id = str(uuid.uuid4())
    client_hash = get_password_hash("client123")
    
    cursor.execute("""
    INSERT INTO users (id, email, password_hash, first_name, last_name, user_type,
                      is_active, is_verified, compliance_status, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (client_id, "client@example.com", client_hash, "Test", "Client", "client",
          1, 1, "approved", now, now))
    
    print("[OK] Client user created")
    print(f"    ID: {client_id}")
    print("    Email: client@example.com")
    print("    Password: client123")
    print("    Type: client")
    print()
    
    conn.commit()
    conn.close()
    
    print("[SUCCESS] Users ready to login!")
    print()
    print("Test with backend API...")
    
    import requests
    response = requests.post(
        "http://127.0.0.1:8000/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "admin123"},
        timeout=10
    )
    
    if response.status_code == 200:
        print("[OK] Login endpoint works!")
        print(f"    Status: {response.status_code}")
        print(f"    Token: {response.json().get('access_token', 'N/A')[:30]}...")
    else:
        print(f"[WARNING] Login returned {response.status_code}")
        print(f"    Response: {response.text[:200]}")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

