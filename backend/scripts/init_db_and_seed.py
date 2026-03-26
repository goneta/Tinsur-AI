import sys
import os

# Add parent dir to path (backend)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
# Import models so they are registered with Base
import app.models 

# Import the seed function
from scripts.seed_full_quote_wizard import seed_full_wizard_data

def init_db():
    print("Creating all tables via SQLAlchemy...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
    
    print("Starting seed...")
    seed_full_wizard_data()

if __name__ == "__main__":
    init_db()
