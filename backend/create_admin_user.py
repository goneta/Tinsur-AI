
import sys
import os
from dotenv import load_dotenv
load_dotenv() # Load env vars before importing config/db

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.models.company import Company
from app.models.user import User
from app.models.client import Client
from app.models.policy import Policy
from app.models.endorsement import Endorsement
from app.models.regulatory import IFRS17Group
# Add RBAC imports
from app.models.rbac import Role, Permission
from app.core.security import get_password_hash
import uuid

def create_admin():
    # Ensure tables exist
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Ensure Company Exists
        company_name = "Demo Insurance Co"
        domain = "demoinsurance.com"
        
        company = db.query(Company).filter(Company.subdomain == domain).first()
        if not company:
            print(f"Creating company: {company_name}")
            company = Company(
                name=company_name,
                subdomain=domain,
                email=f"contact@{domain}",
                is_active=True,
                currency="XOF",
                country="Côte d'Ivoire"
            )
            db.add(company)
            db.commit()
            db.refresh(company)
        else:
            print(f"Company verified: {company.name}")

        # 2. Re-Confirm/Create Roles
        print("\nSeeding RBAC Roles...")
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

        # 3. Re-Confirm/Create Permissions
        print("Seeding RBAC Permissions...")
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

        # 4. Ensure Admin User Exists
        email = f"admin@{domain}"
        password = "admin123"
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"\nCreating admin user: {email}")
            user = User(
                email=email,
                password_hash=get_password_hash(password),
                first_name="Super",
                last_name="Admin",
                role="super_admin",
                company_id=company.id,
                is_active=True,
                is_verified=True
            )
            db.add(user)
        else:
            print(f"\nResetting admin user: {email}")
            user.password_hash = get_password_hash(password)
            user.is_active = True
            user.is_verified = True
            user.role = "super_admin"
            
        db.commit()
        print("Admin user ready.")
        print(f"Email: {email}")
        print(f"Password: {password}")

    except Exception as e:
        print(f"Error creating admin/data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
