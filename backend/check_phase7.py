from sqlalchemy import create_engine, inspect
from app.core.config import settings

def check_phase7():
    database_url = settings.DATABASE_URL
    engine = create_engine(database_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    expected = [
        'inter_company_shares',
        'tickets',
        'referrals',
        'loyalty_points',
        'telematics_data',
        'ml_models',
        'settings'
    ]
    
    print("Checking tables...")
    for t in expected:
        exists = t in tables
        print(f"{t}: {'OK' if exists else 'MISSING'}")

if __name__ == "__main__":
    check_phase7()
