
from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL)

def update_claims_schema():
    with engine.connect() as conn:
        logger.info("Adding ai_assessment column to claims table...")
        conn.execute(text("COMMIT"))
        
        try:
            conn.execute(text("ALTER TABLE claims ADD COLUMN ai_assessment JSON"))
            logger.info("Successfully added ai_assessment column.")
        except Exception as e:
            logger.warning(f"Failed to add column (likely exists): {e}")

if __name__ == "__main__":
    update_claims_schema()
