
import sys
import os

# Set up path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.client import Client
import uuid

def debug_user():
    db = SessionLocal()
    try:
        email = "test_client@tinsur.ai"
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User {email} NOT FOUND.")
            return

        print(f"✅ User Found:")
        print(f"   ID: {user.id}")
        print(f"   Role: {user.role}")
        print(f"   Company ID: {user.company_id}")
        
        client = db.query(Client).filter(Client.user_id == user.id).first()
        if client:
             print(f"✅ Client Found:")
             print(f"   ID: {client.id}")
             print(f"   User ID: {client.user_id}")
             print(f"   Company ID: {client.company_id}")
             
             if str(client.company_id) != str(user.company_id):
                 print(f"❌ MISMATCH: Client Company ({client.company_id}) != User Company ({user.company_id})")
             else:
                 print(f"✅ Company IDs Match.")
        else:
             print(f"❌ Client NOT FOUND for User ID {user.id}")
             
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_user()
