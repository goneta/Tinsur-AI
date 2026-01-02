
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
try:
    user = db.query(User).filter(User.email == "admin@demoinsurance.com").first()
    if user:
        print(f"User: {user.email}")
        print(f"Role: {user.role}")
        print(f"ID: {user.id}")
        print(f"Company ID: {user.company_id}")
    else:
        print("User not found")
finally:
    db.close()
