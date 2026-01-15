
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import SessionLocal

def update_driver_schema_v2():
    db = SessionLocal()
    try:
        print("Starting Driver Schema Update V2...")
        
        # Add new columns
        new_columns = [
            ("first_name", "VARCHAR(50)"),
            ("last_name", "VARCHAR(50)"),
            ("city", "VARCHAR(100)"),
            ("postal_code", "VARCHAR(20)"),
            ("country", "VARCHAR(100)"),
            ("driving_license_url", "VARCHAR(500)")
        ]
        
        for col_name, col_type in new_columns:
            # Check if column exists
            check_query = text(f"SELECT column_name FROM information_schema.columns WHERE table_name='client_drivers' AND column_name='{col_name}'")
            result = db.execute(check_query)
            if not result.fetchone():
                print(f"Adding column {col_name}...")
                db.execute(text(f"ALTER TABLE client_drivers ADD COLUMN {col_name} {col_type}"))
            else:
                print(f"Column {col_name} already exists.")

        db.commit()
        print("Schema update completed successfully.")
            
    except Exception as e:
        print(f"Error updating database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_driver_schema_v2()
