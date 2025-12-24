
from sqlalchemy import create_engine, text, inspect
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL)
logger.info(f"Connecting to database: {settings.DATABASE_URL}")

def update_schema():
    with engine.connect() as conn:
        logger.info("Migrating schema...")
        conn.execute(text("COMMIT"))
        
        # 1. Alter inter_company_shares
        alter_statements = [
            "ALTER TABLE inter_company_shares ADD COLUMN scope VARCHAR(10) DEFAULT 'B2B'",
            "ALTER TABLE inter_company_shares ADD COLUMN is_reshareable BOOLEAN DEFAULT FALSE",
            "ALTER TABLE inter_company_shares ADD COLUMN reshare_rule VARCHAR(1)",
            "ALTER TABLE inter_company_shares ADD COLUMN to_client_id UUID",
            "ALTER TABLE inter_company_shares ADD COLUMN to_user_id UUID",
            "ALTER TABLE inter_company_shares ADD COLUMN document_id UUID",
            # Fix for documents table missing columns
            "ALTER TABLE documents ADD COLUMN scope VARCHAR(20) DEFAULT 'B2B'",
            "ALTER TABLE documents ADD COLUMN is_shareable BOOLEAN DEFAULT FALSE",
            "ALTER TABLE documents ADD COLUMN reshare_rule VARCHAR(1) DEFAULT 'C'",
            "ALTER TABLE documents ADD COLUMN visibility VARCHAR(20) DEFAULT 'PRIVATE'",
            # AI Subscription columns
            "ALTER TABLE companies ADD COLUMN ai_plan VARCHAR(50) DEFAULT 'CREDIT'",
            "ALTER TABLE companies ADD COLUMN ai_api_key_encrypted VARCHAR(255)",
            "ALTER TABLE companies ADD COLUMN ai_credits_balance FLOAT DEFAULT 0.0"
        ]
        
        for stmt in alter_statements:
            try:
                conn.execute(text(stmt))
                logger.info(f"Executed: {stmt}")
            except Exception as e:
                logger.warning(f"Skipped (likely exists): {stmt} -> {e}")

    # Inspect before
    insp = inspect(engine)
    existing_tables = insp.get_table_names()
    logger.info(f"Tables BEFORE: {existing_tables}")

    # Create share_codes table
    try:
        from app.models.share_code import ShareCode
        ShareCode.__table__.create(bind=engine, checkfirst=True)
        logger.info("Created share_codes table (if missing).")
    except Exception as e:
        logger.error(f"Error creating share_codes table: {e}")

    # Create documents table
    try:
        from app.models.document import Document
        Document.__table__.create(bind=engine, checkfirst=True)
        logger.info("Created documents table (if missing).")
    except Exception as e:
        logger.error(f"Error creating documents table: {e}")
        import traceback
        traceback.print_exc()

    # Create AI Subscription tables
    try:
        from app.models.system_settings import SystemSettings, AiUsageLog
        SystemSettings.__table__.create(bind=engine, checkfirst=True)
        AiUsageLog.__table__.create(bind=engine, checkfirst=True)
        logger.info("Created system_settings and ai_usage_logs tables (if missing).")
    except Exception as e:
        logger.error(f"Error creating AI subscription tables: {e}")
        import traceback
        traceback.print_exc()

    # Inspect after
    insp = inspect(engine)
    final_tables = insp.get_table_names()
    logger.info(f"Tables AFTER: {final_tables}")
    
    if "documents" in final_tables:
        logger.info("SUCCESS: 'documents' table exists.")
    else:
        logger.error("FAILURE: 'documents' table is STILL MISSING.")

if __name__ == "__main__":
    update_schema()
