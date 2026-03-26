import sys
import os
import random
import uuid
from datetime import date, timedelta
from decimal import Decimal

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.chdir(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal
from app.models.client import Client
from app.models.client_details import ClientAutomobile

def seed_vehicles():
    db = SessionLocal()
    try:
        clients = db.query(Client).all()
        print(f"Found {len(clients)} clients.")
        
        count = 0
        existing_count = 0
        
        vehicle_makes = [
            ("Toyota", "Corolla", 2018),
            ("Toyota", "Yaris", 2015),
            ("Honda", "Civic", 2019),
            ("Hyundai", "Tucson", 2020),
            ("Kia", "Sportage", 2021),
            ("Peugeot", "3008", 2019),
            ("Renault", "Duster", 2017),
            ("Ford", "Ranger", 2021)
        ]
        
        for client in clients:
            # Check if exists
            existing = db.query(ClientAutomobile).filter_by(client_id=client.id).first()
            if existing:
                existing_count += 1
                continue
            
            make, model, year = random.choice(vehicle_makes)
            
            # Generate VIN
            vin = f"VN{random.randint(10000000, 99999999)}"
            reg = f"CI-{random.randint(1000, 9999)}-{random.choice(['AB', 'CD', 'EF'])}"
            
            vehicle = ClientAutomobile(
                id=uuid.uuid4(),
                client_id=client.id,
                vehicle_registration=reg,
                vehicle_make=make,
                vehicle_model=model,
                vehicle_year=year,
                vehicle_value=Decimal(random.randint(5, 15) * 1000000), # 5M to 15M
                vehicle_mileage=float(random.randint(10000, 100000)),
                engine_capacity_cc=random.choice([1600, 2000, 2500]),
                fuel_type=random.choice(["Petrol", "Diesel"]),
                vehicle_usage="Private",
                seat_count=5,
                chassis_number=vin,
                vehicle_color=random.choice(["White", "Black", "Silver", "Blue"]),
                country_of_registration="Côte d'Ivoire",
                
                # Driver Details (Default to client)
                driver_name=f"{client.first_name} {client.last_name}",
                driver_dob=client.date_of_birth,
                license_number=f"LIC-{random.randint(100000, 999999)}",
                license_issue_date=date(2015, 1, 1),
                license_expiry_date=date(2030, 1, 1),
                license_category="B",
                driving_experience_years=random.randint(2, 15),
                
                accident_count=0,
                claim_count=0
            )
            
            db.add(vehicle)
            count += 1
            
        db.commit()
        print(f"Added vehicles for {count} clients.")
        print(f"Skipped {existing_count} clients (already had vehicles).")

    except Exception as e:
        print(f"Error seeding vehicles: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_vehicles()
