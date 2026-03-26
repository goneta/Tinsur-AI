import sys
import sqlite3
import uuid

# Import the same password hashing used by backend
sys.path.insert(0, "backend")

try:
    from app.core.security import get_password_hash
    
    db_path = "backend/insurance.db"
    
    print("[*] Using backend password hashing")
    print()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create admin user with proper hash
    admin_id = str(uuid.uuid4())
    admin_pass_hash = get_password_hash("admin123")
    
    cursor.execute("DELETE FROM users WHERE email = ?", ("admin@example.com",))
    
    cursor.execute("""
    INSERT INTO users (id, email, password_hash, first_name, last_name, is_active, is_superuser, role)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (admin_id, "admin@example.com", admin_pass_hash, "Admin", "User", 1, 1, "admin"))
    
    print("[OK] Admin user created with proper password hash")
    
    # Create client user
    client_id = str(uuid.uuid4())
    client_pass_hash = get_password_hash("client123")
    
    cursor.execute("DELETE FROM users WHERE email = ?", ("client@example.com",))
    
    cursor.execute("""
    INSERT INTO users (id, email, password_hash, first_name, last_name, is_active, is_superuser, role)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (client_id, "client@example.com", client_pass_hash, "Test", "Client", 1, 0, "user"))
    
    print("[OK] Client user created with proper password hash")
    
    conn.commit()
    conn.close()
    
    print()
    print("[OK] Database ready for login!")
    print()
    print("Login credentials:")
    print("  Email: admin@example.com")
    print("  Password: admin123")
    
except ImportError as e:
    print(f"[ERROR] Could not import backend modules: {e}")
    print()
    print("Falling back to simple SHA256 hashes...")
    
    import hashlib
    import sqlite3
    import uuid
    
    db_path = "backend/insurance.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Use SHA256 as fallback (won't work with backend but at least DB is updated)
    admin_id = str(uuid.uuid4())
    admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
    
    cursor.execute("DELETE FROM users WHERE email = ?", ("admin@example.com",))
    cursor.execute("""
    INSERT INTO users (id, email, password_hash, first_name, last_name, is_active, is_superuser, role)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (admin_id, "admin@example.com", admin_hash, "Admin", "User", 1, 1, "admin"))
    
    conn.commit()
    conn.close()
    
    print("[WARNING] Using SHA256 - may not work with backend")

