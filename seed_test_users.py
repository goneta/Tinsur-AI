#!/usr/bin/env python
"""Seed test users in Tinsur-AI database for Phase 1 testing"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.security import get_password_hash
from datetime import datetime
import uuid

# Database connection
DATABASE_URL = "sqlite:///./insurance.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_users():
    """Create test users in database"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("SEEDING TEST USERS FOR PHASE 1")
        print("=" * 60)
        print()
        
        # Check if users already exist
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        client_user = db.query(User).filter(User.email == "client@example.com").first()
        
        if admin_user:
            print("[OK] Admin user already exists")
        else:
            print("Creating admin user...")
            admin = User(
                id=uuid.uuid4(),
                email="admin@example.com",
                first_name="Admin",
                last_name="User",
                password_hash=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True,
                is_staff=True,
                role="admin",
                created_at=datetime.utcnow()
            )
            db.add(admin)
            db.commit()
            print("[OK] Admin user created")
            print(f"    Email: admin@example.com")
            print(f"    Password: admin123")
            print(f"    ID: {admin.id}")
        
        if client_user:
            print("[OK] Client user already exists")
        else:
            print("Creating client user...")
            client = User(
                id=uuid.uuid4(),
                email="client@example.com",
                first_name="Test",
                last_name="Client",
                password_hash=get_password_hash("client123"),
                is_active=True,
                is_superuser=False,
                is_staff=False,
                role="user",
                created_at=datetime.utcnow()
            )
            db.add(client)
            db.commit()
            print("[OK] Client user created")
            print(f"    Email: client@example.com")
            print(f"    Password: client123")
            print(f"    ID: {client.id}")
        
        print()
        print("=" * 60)
        print("USERS READY FOR TESTING")
        print("=" * 60)
        print()
        print("Use these credentials to login:")
        print()
        print("Admin:")
        print("  POST /api/v1/auth/login")
        print("  { \"email\": \"admin@example.com\", \"password\": \"admin123\" }")
        print()
        print("Client:")
        print("  POST /api/v1/auth/login")
        print("  { \"email\": \"client@example.com\", \"password\": \"client123\" }")
        print()
        
        # List all users in database
        all_users = db.query(User).all()
        print(f"Total users in database: {len(all_users)}")
        for user in all_users:
            print(f"  - {user.email} (role: {user.role})")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to seed users: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = seed_users()
    sys.exit(0 if success else 1)
