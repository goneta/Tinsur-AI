from app.core.database import engine, Base
from app.models.client_details import ClientAutomobile, ClientHousing, ClientHealth, ClientLife

def init_tables():
    print("Creating policy-specific client tables...")
    try:
        # This will create tables that don't exist yet
        ClientAutomobile.__table__.create(bind=engine, checkfirst=True)
        ClientHousing.__table__.create(bind=engine, checkfirst=True)
        ClientHealth.__table__.create(bind=engine, checkfirst=True)
        ClientLife.__table__.create(bind=engine, checkfirst=True)
        print("Successfully created/verified tables.")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    init_tables()
