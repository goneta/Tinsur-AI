from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.rbac import Role, Permission

def check_rbac():
    db = SessionLocal()
    try:
        roles = db.query(Role).all()
        print(f"Total Roles: {len(roles)}")
        for r in roles:
            print(f"Role: {r.name}, Permissions: {len(r.permissions)}")
            for p in r.permissions:
                print(f"  - {p.scope}:{p.action}")
                
        permissions = db.query(Permission).all()
        print(f"\nTotal Permissions: {len(permissions)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_rbac()
