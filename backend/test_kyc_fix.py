import asyncio
from sqlalchemy import create_client
from sqlalchemy.orm import sessionmaker
from app.services.ai_service import AiService
from app.core.database import SessionLocal
import os

async def test_kyc_no_company():
    db = SessionLocal()
    try:
        ai_service = AiService(db)
        print("Testing get_effective_ai_config() with no arguments...")
        try:
            config = ai_service.get_effective_ai_config()
            print(f"Config retrieved: {len(config[0]) > 0 if config[0] else 'No API Key'}")
        except TypeError as e:
            print(f"TypeError still exists: {e}")
            return
            
        print("Testing parse_kyc_document_bytes() call structure...")
        # We won't actually call Gemini here (mock would be better, but we just check the structure)
        # If it reached genai.configure, then the TypeError is gone.
        try:
            # Passing empty bytes will likely fail Gemini but we want to see if it hits the TypeError first
            await ai_service.parse_kyc_document_bytes(b"", "identity_document")
        except TypeError as e:
            if "get_effective_ai_config" in str(e):
                print(f"TypeError in parse_kyc_document_bytes: {e}")
            else:
                print(f"Other TypeError: {e}")
        except Exception as e:
            print(f"Caught expected exception (since bytes are empty): {type(e).__name__}")
            
        print("Test complete.")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_kyc_no_company())
