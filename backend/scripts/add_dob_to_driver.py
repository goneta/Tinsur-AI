
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import SessionLocal
from app.core.config import settings

def add_dob_to_driver():
    db = SessionLocal()
    try:
        # Check if column exists
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='client_drivers' AND column_name='date_of_birth'"))
        if not result.fetchone():
            print("Adding date_of_birth column to client_drivers table...")
            db.execute(text("ALTER TABLE client_drivers ADD COLUMN date_of_birth DATE"))
            db.commit()
            print("Column added successfully.")
        else:
            print("Column date_of_birth already exists.")
            
    except Exception as e:
        print(f"Error updating database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_dob_to_driver()
