
from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL)

def update_payroll_schema():
    with engine.connect() as conn:
        logger.info("Updating payroll_transactions table...")
        conn.execute(text("COMMIT"))
        
        try:
            conn.execute(text("ALTER TABLE payroll_transactions ADD COLUMN payment_month VARCHAR(20)"))
            logger.info("Added payment_month column to payroll_transactions.")
        except Exception as e:
            logger.warning(f"Could not add column (likely already exists): {e}")

if __name__ == "__main__":
    update_payroll_schema()
