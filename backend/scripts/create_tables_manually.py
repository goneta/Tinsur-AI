import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from app.models.policy_service import PolicyService, policy_service_association

def create_tables():
    print("Creating tables manually...")
    try:
        PolicyService.__table__.create(bind=engine, checkfirst=True)
        print("Created policy_services table.")
        policy_service_association.create(bind=engine, checkfirst=True)
        print("Created policy_service_association table.")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()
