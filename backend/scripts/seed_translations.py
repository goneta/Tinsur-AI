
import json
import os
import sys
from glob import glob

# Add parent directory to path to allow importing app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.translation import Translation

def seed_translations():
    db = SessionLocal()
    
    # Path to translation JSON files
    base_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "ai_docs", "references", "examples", "insurance_docs", "translation"
    )
    
    json_files = glob(os.path.join(base_path, "*.json"))
    
    print(f"Found {len(json_files)} translation files in {base_path}")
    
    count_en = 0
    count_fr = 0
    
    for file_path in json_files:
        print(f"Processing {os.path.basename(file_path)}...")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            for key, value in data.items():
                if not key or not value:
                    continue
                    
                # Upsert English (Key -> Key)
                existing_en = db.query(Translation).filter(
                    Translation.key == key,
                    Translation.language_code == "en"
                ).first()
                
                if not existing_en:
                    db.add(Translation(key=key, language_code="en", value=key, group="common"))
                    count_en += 1
                
                # Upsert French (Key -> Value)
                existing_fr = db.query(Translation).filter(
                    Translation.key == key,
                    Translation.language_code == "fr"
                ).first()
                
                if not existing_fr:
                    db.add(Translation(key=key, language_code="fr", value=value, group="common"))
                    count_fr += 1
                elif existing_fr.value != value:
                    existing_fr.value = value # Update if changed
                    
            db.commit()
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            db.rollback()
            
    print(f"Seeding complete. Added {count_en} English entries and {count_fr} French entries.")
    db.close()

if __name__ == "__main__":
    seed_translations()
