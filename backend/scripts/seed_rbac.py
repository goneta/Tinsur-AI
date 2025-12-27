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
from app.models.rbac import Role, Permission

def seed_rbac():
    db = SessionLocal()
    try:
        print("Seeding RBAC...")
        
        # 1. Define Permissions
        permissions_map = {
            "quote:read": "View quotes",
            "quote:create": "Create quote",
            "policy:read": "View policies",
            "policy:write": "Modify policies",
            "policy:create": "Create policy",
            "claim:read": "View claims",
            "claim:write": "Modify claims",
            "claim:create": "Create claim",
            "payment:create": "Make payment",
            "collaboration:share": "Share document in collaboration hub",
            "employee:create": "Create employee",
            "client:create": "Create client",
            "payroll:run": "Do payroll",
            "template:create": "Create policy template",
            "pos:create": "Create POS",
            "ticket:create": "Create support ticket",
            "telematics:access": "Access Telematics & UBI",
            "telematics:create": "Create Telematics & UBI",
            "ai_manager:access": "Use AI Agent Manager",
            "admin:read": "View User permissions",
            "admin:write": "Manage User permissions",
            "settings:write": "Update Company Information",
            "analytics:view": "Access analytics dashboard",
            "analytics:export": "Export reports",
            "financials:view": "Access financial reports",
            "financials:manage": "Process payments and manage accounts",
            "users:view": "View employee list",
            "users:manage": "Create and edit users",
            "settings:view": "View company settings",
            "settings:manage": "Edit company settings",
            "pos:manage": "Manage POS locations and inventory",
            "admin:access": "Access admin dashboard"
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
            elif perm.description != desc:
                perm.description = desc
                db.commit()
                db.refresh(perm)
                print(f"Updated Description for: {key}")
            db_perms[key] = perm

        # 2. Define Roles
        roles_def = {
            "client": ["quote:read", "quote:create", "claim:read", "claim:write", "policy:read", "ticket:create"],
            "agent": [
                "quote:read", "quote:create", "claim:read", "claim:write", 
                "policy:read", "policy:write", "policy:create", 
                "client:create", "ticket:create", "telematics:access", "ai_manager:access"
            ],
            "manager": [
                "quote:read", "quote:create", "claim:read", "claim:write", 
                "policy:read", "policy:write", "policy:create",
                "payment:create", "collaboration:share", "employee:create",
                "client:create", "payroll:run", "template:create", "pos:create",
                "ticket:create", "telematics:access", "ai_manager:access",
                "admin:read"
            ],
            "receptionist": ["quote:read", "client:create", "ticket:create"],
            "company_admin": "ALL", 
            "super_admin": "ALL"
        }

        # Fetch ALL permissions for "ALL" assignment
        all_perms = db.query(Permission).all()
        all_perms_map = {p.key: p for p in all_perms}

        for role_name, perms_list in roles_def.items():
            role = db.query(Role).filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, description=f"Default {role_name} role")
                db.add(role)
                db.commit()
                db.refresh(role)
                print(f"Created Role: {role_name}")
            
            # Sync permissions
            target_perms = all_perms if perms_list == "ALL" else [all_perms_map[pk] for pk in perms_list if pk in all_perms_map]
            
            # Ensure Admin roles have everything
            current_perm_ids = set(p.id for p in role.permissions)
            added_count = 0
            for p in target_perms:
                if p.id not in current_perm_ids:
                    role.permissions.append(p)
                    added_count += 1
            
            if added_count > 0:
                print(f"Assigned {added_count} new permissions to {role_name}")
                db.commit()
            
        print("RBAC Seeding Complete.")

    except Exception as e:
        print(f"Error seeding RBAC: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_rbac()
