import sys
import os
sys.path.append(os.getcwd())
from app.core.database import Base, SessionLocal
from app.models.rbac import Role, Permission
from sqlalchemy.orm import configure_mappers

print("Imports done.")
try:
    configure_mappers()
    print("Mappers configured.")
except Exception as e:
    print(f"Error: {e}")
