
import sys
import os
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine

# Explicit imports to ensure mapping (and valid syntax)
from app.models.rbac import Role, Permission
from app.models.user import User
from app.models.company import Company

def seed_rbac():
    # Ensure tables exist (just in case)
    print("Checking database/tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Seeding RBAC Roles and Permissions...")
        
        # 1. Define Roles
        roles_to_create = [
            {"name": "super_admin", "description": "Full system access"},
            {"name": "company_admin", "description": "Admin for a specific company"},
            {"name": "manager", "description": "Team manager with approval rights"},
            {"name": "agent", "description": "Standard insurance agent"},
            {"name": "client", "description": "End customer / Policy holder"},
            {"name": "employee", "description": "Standard company employee (non-agent)"},
            {"name": "underwriter", "description": "Underwriting authority"}
        ]
        
        for r_data in roles_to_create:
            role = db.query(Role).filter(Role.name == r_data["name"]).first()
            if not role:
                print(f"Creating Role: {r_data['name']}")
                role = Role(name=r_data["name"], description=r_data["description"])
                db.add(role)
        db.commit()

        # 2. Define Permissions
        scopes = ['policy', 'quote', 'claim', 'client', 'payment', 'document', 'report', 'admin', 'dashboard']
        actions = ['read', 'write', 'create', 'delete', 'approve', 'manage']
        
        for scope in scopes:
            for action in actions:
                perm_key = f"{scope}:{action}"
                perm = db.query(Permission).filter(Permission.scope == scope, Permission.action == action).first()
                if not perm:
                    perm = Permission(scope=scope, action=action, description=f"Can {action} {scope}s")
                    db.add(perm)
        db.commit()
        
        print("RBAC Seed Completed Successfully.")
        
    except Exception as e:
        print(f"Error seeding RBAC: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_rbac()
