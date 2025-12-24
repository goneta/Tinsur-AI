
import asyncio
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import settings
from app.models.rbac import Role, Permission

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_rbac():
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
            {"name": "employee", "description": "Standard company employee (non-agent)"}
        ]
        
        roles_map = {}
        for r_data in roles_to_create:
            role = db.query(Role).filter(Role.name == r_data["name"]).first()
            if not role:
                print(f"Creating Role: {r_data['name']}")
                role = Role(name=r_data["name"], description=r_data["description"])
                db.add(role)
            roles_map[r_data["name"]] = role
        db.commit()

        # 2. Define Sample Permissions
        scopes = ['policy', 'quote', 'claim', 'client', 'payment', 'document', 'report']
        actions = ['read', 'write', 'create', 'delete', 'approve']
        
        permissions_list = []
        for scope in scopes:
            for action in actions:
                # Skip some unlikely ones
                if scope == 'report' and action in ['create', 'delete']: continue
                
                perm_key = f"{scope}:{action}"
                perm = db.query(Permission).filter(Permission.scope == scope, Permission.action == action).first()
                if not perm:
                    # print(f"Creating Permission: {perm_key}")
                    perm = Permission(scope=scope, action=action, description=f"Can {action} {scope}s")
                    db.add(perm)
                permissions_list.append(perm)
        db.commit()
        
        print("RBAC Seed Completed.")
        
    except Exception as e:
        print(f"Error seeding RBAC: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_rbac()
