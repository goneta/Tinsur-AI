import sys
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.rbac import Role, Permission

def check_users():
    db = SessionLocal()
    try:
        roles = db.query(Role).all()
        permissions = db.query(Permission).all()
        print(f"Total Roles in DB: {len(roles)}")
        print(f"Total Permissions in DB: {len(permissions)}")
        for p in permissions:
            print(f"Permission: {p.key} - {p.description}")
        
        users = db.query(User).all()
        print(f"Total Users: {len(users)}")
        for u in users:
            print(f"User: {u.email}, Role: {u.role}")
            # Check if role exists in roles table
            r = db.query(Role).filter(Role.name == u.role).first()
            if r:
                print(f"  Matches Role in DB: {r.name}")
            else:
                print(f"  WARNING: Role '{u.role}' NOT found in roles table!")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
