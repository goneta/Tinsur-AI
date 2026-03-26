import sys
import os
from decimal import Decimal
import uuid
from sqlalchemy import text

# Add parent directory to path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal

def seed_policy_services_raw():
    db = SessionLocal()
    try:
        print("Seeding Policy Services (Raw SQL)...")
        # Get companies
        result = db.execute(text("SELECT id, name FROM companies"))
        companies = result.fetchall()
        
        if not companies:
            print("No companies found.")
            return

        # Services to add
        services_data = [
            {"name_en": "Comprehensive cover", "name_fr": "Couverture tous risques", "default_price": 0.00, "description": "Full coverage for your vehicle."},
            {"name_en": "Small courtesy car", "name_fr": "Véhicule de courtoisie (petit modèle)", "default_price": 2.50, "description": "Access to a small courtesy car."},
            {"name_en": "Upgraded courtesy car", "name_fr": "Véhicule de courtoisie amélioré", "default_price": 5.00, "description": "Access to a higher-class courtesy car."},
            {"name_en": "90-day comprehensive EU cover", "name_fr": "Couverture tous risques dans l’UE pendant 90 jours", "default_price": 3.00, "description": "Full coverage while driving in Europe for 90 days."},
            {"name_en": "Windscreen cover", "name_fr": "Garantie bris de glace", "default_price": 1.50, "description": "Coverage for windscreen damage."},
            {"name_en": "Uninsured driver promise", "name_fr": "Garantie conducteur non assuré", "default_price": 2.00, "description": "Protection if hit by an uninsured driver."},
            {"name_en": "Loss of keys", "name_fr": "Perte de clés", "default_price": 1.20, "description": "Coverage for lost keys."},
            {"name_en": "Claims portal access", "name_fr": "Accès au portail de déclaration de sinistre", "default_price": 0.00, "description": "Online access to manage claims."},
            {"name_en": "Personal accident cover", "name_fr": "Garantie individuelle accident", "default_price": 4.00, "description": "Compensation for injury or death."},
            {"name_en": "Personal belongings cover", "name_fr": "Garantie effets personnels", "default_price": 2.50, "description": "Coverage for items inside the vehicle."},
            {"name_en": "Manufacturer-fitted audio equipment / sat nav", "name_fr": "Équipement audio / GPS monté par le constructeur", "default_price": 1.50, "description": "Coverage for built-in audio/nav equipment."},
            {"name_en": "Audio equipment / sat nav", "name_fr": "Équipement audio / GPS", "default_price": 2.00, "description": "Coverage for portable audio/nav equipment."},
            {"name_en": "Driving other cars (conditional)", "name_fr": "Conduite d’autres véhicules (sous conditions)", "default_price": 3.50, "description": "Allows driving other vehicles with third-party cover."},
            {"name_en": "Car seats cover", "name_fr": "Garantie sièges auto", "default_price": 1.80, "description": "Coverage for child car seats."},
            {"name_en": "Theft of keys", "name_fr": "Vol de clés", "default_price": 1.50, "description": "Coverage for stolen keys."},
            {"name_en": "New car replacement", "name_fr": "Remplacement du véhicule neuf", "default_price": 6.00, "description": "Replaces car with a new model if totaled within first year."},
            {"name_en": "Misfuelling cover", "name_fr": "Garantie erreur de carburant", "default_price": 1.20, "description": "Coverage for engine damage from wrong fuel."},
            {"name_en": "Onward travel", "name_fr": "Garantie poursuite du voyage", "default_price": 2.20, "description": "Assistance to continue journey after breakdown."},
            {"name_en": "Vandalism promise", "name_fr": "Garantie vandalisme", "default_price": 2.50, "description": "No loss of NCD for vandalism claims."},
            {"name_en": "Hotel expenses", "name_fr": "Frais d’hébergement", "default_price": 1.50, "description": "Covers hotel costs after an accident far from home."}
        ]

        for company in companies:
            c_id = company[0]  # id
            c_name = company[1] # name
            print(f"Seeding for company: {c_name} ({c_id})")
            
            for data in services_data:
                # Check if exists
                check_sql = text("SELECT id FROM policy_services WHERE company_id = :cid AND name_en = :name")
                # Handle UUID conversion if needed (but raw sql with string param usually works on sqlite if stored as string)
                # If stored as blob/uuid type, might need casting. But let's assume string or compatible.
                existing = db.execute(check_sql, {"cid": str(c_id), "name": data["name_en"]}).fetchone()
                
                if not existing:
                    new_id = str(uuid.uuid4())
                    insert_sql = text("""
                        INSERT INTO policy_services (id, company_id, name_en, name_fr, default_price, description, is_active)
                        VALUES (:id, :cid, :name_en, :name_fr, :price, :desc, 1)
                    """)
                    db.execute(insert_sql, {
                        "id": new_id,
                        "cid": str(c_id),
                        "name_en": data["name_en"],
                        "name_fr": data["name_fr"],
                        "price": data["default_price"],
                        "desc": data["description"]
                    })
                    print(f" - Added: {data['name_en']}")
                else:
                    print(f" - Skipped: {data['name_en']}")
        
        db.commit()
        print("Done.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_policy_services_raw()
