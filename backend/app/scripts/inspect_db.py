from sqlalchemy import create_engine, inspect
from app.core.config import settings

def inspect_db():
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    print("Existing Tables:")
    tables = inspector.get_table_names()
    for table in sorted(tables):
        print(f"- {table}")
        
    required_phase7 = [
        'claims', 'inter_company_shares', 'tickets', 'referrals', 
        'loyalty_points', 'telematics_data', 'ml_models'
    ]
    
    print("\nPhase 7 / Missing Table Status:")
    for table in required_phase7:
        status = "EXISTS" if table in tables else "MISSING"
        print(f"{table:25}: {status}")

if __name__ == "__main__":
    inspect_db()
