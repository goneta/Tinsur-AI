
from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL)

def update_clients_kyc_schema():
    with engine.connect() as conn:
        logger.info("Adding KYC columns to clients table...")
        conn.execute(text("COMMIT"))
        
        statements = [
            "ALTER TABLE clients ADD COLUMN IF NOT EXISTS kyc_notes TEXT",
            "ALTER TABLE clients ADD COLUMN IF NOT EXISTS kyc_results JSON DEFAULT '{}'"
        ]
        
        for stmt in statements:
            try:
                conn.execute(text(stmt))
                logger.info(f"Executed: {stmt}")
            except Exception as e:
                logger.warning(f"Error: {stmt} -> {e}")

if __name__ == "__main__":
    update_clients_kyc_schema()
