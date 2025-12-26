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
            {
                "name_en": "Courtesy Car",
                "name_fr": "Véhicule de remplacement",
                "default_price": 50.00,
                "description": "Provision of a courtesy car while yours is being repaired."
            },
            {
                "name_en": "Windscreen Cover",
                "name_fr": "Couverture pare-brise",
                "default_price": 25.00,
                "description": "Coverage for windscreen repair or replacement."
            },
            {
                "name_en": "£5,000 Personal Accident Cover",
                "name_fr": "Couverture accident personnel de 5 000 £",
                "default_price": 15.00,
                "description": "Personal accident cover up to £5,000."
            },
            {
                "name_en": "No Claims Discount Protection",
                "name_fr": "Protection du bonus sans sinistre",
                "default_price": 30.00,
                "description": "Protect your No Claims Discount even if you make a claim."
            },
            {
                "name_en": "RAC Roadside Only Breakdown Cover",
                "name_fr": "Assistance routière RAC (dépannage sur place uniquement)",
                "default_price": 40.00,
                "description": "Roadside assistance provided by RAC."
            },
            {
                "name_en": "Legal Cover",
                "name_fr": "Protection juridique",
                "default_price": 20.00,
                "description": "Coverage for legal expenses."
            }
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
