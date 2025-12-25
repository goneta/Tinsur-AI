import sys
import os
import uuid
from dotenv import load_dotenv

# Load env from backend/.env or .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.rbac import Role, Permission
from app.models.user import User

def seed_rbac():
    db = SessionLocal()
    try:
        print("Seeding RBAC...")
        
        # 1. Define Permissions
        permissions_map = {
            "quote:read": "View quotes",
            "quote:create": "Calculate new quotes",
            "claim:read": "View claims",
            "claim:write": "File or update claims",
            "policy:read": "View policies",
            "policy:write": "Create or modify policies",
            "admin:access": "Access admin dashboard",
            "admin:read": "View RBAC settings",
            "admin:write": "Modify RBAC settings"
        }
        
        db_perms = {}
        for key, desc in permissions_map.items():
            scope, action = key.split(":")
            perm = db.query(Permission).filter_by(scope=scope, action=action).first()
            if not perm:
                perm = Permission(scope=scope, action=action, description=desc)
                db.add(perm)
                db.commit()
                db.refresh(perm)
                print(f"Created Permission: {key}")
            db_perms[key] = perm

        # 2. Define Roles
        roles_def = {
            "client": ["quote:read", "quote:create", "claim:read", "claim:write", "policy:read"],
            "agent": ["quote:read", "quote:create", "claim:read", "claim:write", "policy:read", "policy:write"],
            "manager": ["quote:read", "quote:create", "claim:read", "claim:write", "policy:read", "policy:write", "admin:access", "admin:read"],
            "company_admin": list(permissions_map.keys()), # All for now
            "super_admin": list(permissions_map.keys()) # All
        }

        for role_name, perms_list in roles_def.items():
            role = db.query(Role).filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, description=f"Default {role_name} role")
                db.add(role)
                db.commit()
                db.refresh(role)
                print(f"Created Role: {role_name}")
            
            # Sync permissions
            current_perms = set(p.key for p in role.permissions)
            for p_key in perms_list:
                if p_key in current_perms:
                    continue
                perm_obj = db_perms.get(p_key)
                if perm_obj:
                    role.permissions.append(perm_obj)
                    print(f"Assigned {p_key} to {role_name}")
            db.commit()
            
        print("RBAC Seeding Complete.")

    except Exception as e:
        print(f"Error seeding RBAC: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_rbac()
