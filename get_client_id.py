import uuid
from sqlalchemy import create_url
from sqlalchemy.orm import Session
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.database import SessionLocal
from app.models.client import Client

def get_client():
    db = SessionLocal()
    try:
        client = db.query(Client).first()
        if client:
            print(f"CLIENT_ID={client.id}")
        else:
            print("NO_CLIENTS_FOUND")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    get_client()
