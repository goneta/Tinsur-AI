

# Use a mock token or similar if possible, or just rely on public if no auth? 
# The endpoints require auth. I'll need to mock the dependency or login.
# For simplicity in this environment, I'll trust the unit tests or use a script that manually checks DB if I can't easily auth.
# Actually, I can use the same pattern as `verify_coinsurance.py` which likely bypasses auth or has a workaround, 
# or I can just check if the code runs by importing it.

import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Let's create a script that uses the database directly to simulate the API logic to be sure models work,
# as full API testing might need a running server.

from app.core.database import SessionLocal
from app.models.client import Client
from app.models.company import Company
from app.models.client_details import ClientAutomobile
import uuid
from datetime import date

def test_client_details_persistence():
    db = SessionLocal()
    try:
        # 1. Setup Company
        company = db.query(Company).first()
        if not company:
            company = Company(name="Test Company", currency="USD")
            db.add(company)
            db.commit()
            
        # 2. Create Client
        client = Client(
            company_id=company.id,
            client_type="individual",
            first_name="John",
            last_name="Doe",
            email=f"john.doe.{uuid.uuid4()}@example.com",
            phone="1234567890",
            nationality="Ivorian",
            marital_status="Single",
            kyc_status="verified"
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        print(f"Created Client: {client.id} - {client.nationality}")
        
        # 3. Add Automobile Details
        auto_details = ClientAutomobile(
            client_id=client.id,
            vehicle_make="Toyota",
            vehicle_model="Corolla",
            vehicle_year=2022,
            vehicle_value=25000.00,
            chassis_number="VIN123456789"
        )
        db.add(auto_details)
        db.commit()
        db.refresh(client)
        
        # 4. Verify Access via Relationship
        assert client.automobile_details is not None
        assert client.automobile_details.vehicle_make == "Toyota"
        print("Automobile details verified via relationship.")
        
        # 5. Verify housing is None
        assert client.housing_details is None
        print("Housing details verified as None.")
        
    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_client_details_persistence()
