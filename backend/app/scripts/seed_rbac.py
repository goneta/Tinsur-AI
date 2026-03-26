import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.rbac import Role, Permission
from app.models.company import Company
from app.models.pos_location import POSLocation
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default Permissions
# Format: code is "scope:action"
PERMISSIONS = [
    {"scope": "analytics", "action": "view", "description": "Access to analytics dashboard"},
    {"scope": "analytics", "action": "export", "description": "Export reports"},
    {"scope": "financials", "action": "view", "description": "Access to financial reports"},
    {"scope": "financials", "action": "manage", "description": "Process payments and manage accounts"},
    {"scope": "users", "action": "view", "description": "View employee list"},
    {"scope": "users", "action": "manage", "description": "Create and edit users"},
    {"scope": "settings", "action": "view", "description": "View company settings"},
    {"scope": "settings", "action": "manage", "description": "Edit company settings"},
    {"scope": "pos", "action": "manage", "description": "Manage POS locations and inventory"},
]

# Default Roles & Assignments
# Keys match the role strings used in User model
ROLES = {
    "super_admin": ["*"],  # All permissions
    "company_admin": ["*"], # All permissions
    "manager": [
        "analytics:view", "analytics:export",
        "financials:view",
        "users:view", "users:manage",
        "settings:view",
        "pos:manage"
    ],
    "agent": [
        "pos:manage" # Limited POS access
    ],
    "accountant": [
        "financials:view", "financials:manage",
        "analytics:view"
    ]
}

def seed_rbac():
    db = SessionLocal()
    try:
        logger.info("Seeding Permissions...")
        
        # 1. Create Permissions
        db_perms = {}
        for p_data in PERMISSIONS:
            # Check existing using scope+action
            perm = db.query(Permission).filter(
                Permission.scope == p_data["scope"],
                Permission.action == p_data["action"]
            ).first()
            
            if not perm:
                perm = Permission(**p_data)
                db.add(perm)
                db.commit()
                db.refresh(perm)
                logger.info(f"Created Permission: {perm.scope}:{perm.action}")
            
            # Key for lookup
            perm_key = f"{perm.scope}:{perm.action}"
            db_perms[perm_key] = perm
            
        # 2. Create Roles
        for role_name, perm_codes in ROLES.items():
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                role = Role(name=role_name, description=f"Default {role_name} role")
                db.add(role)
                db.commit()
                db.refresh(role)
                logger.info(f"Created Role: {role_name}")
            
            # Assign Permissions
            current_perms = []
            if "*" in perm_codes:
                current_perms = list(db_perms.values())
            else:
                for code in perm_codes:
                    if code in db_perms:
                        current_perms.append(db_perms[code])
                    else:
                        logger.warning(f"Permission code {code} not found for role {role_name}")
            
            # Direct assignment updates the association table
            role.permissions = current_perms
            db.commit()
            logger.info(f"Assigned {len(current_perms)} permissions to {role_name}")

        logger.info("RBAC Seeding Completed Successfully.")
        
    except Exception as e:
        logger.error(f"Error seeding RBAC: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_rbac()
