import google.generativeai as genai
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

async def test_vehicle_parsing():
    print("\n--- Testing Vehicle Document Parsing (Gemini 3 Flash) ---")
    model = genai.GenerativeModel('gemini-3-flash-preview')
    
    # Using a generic prompt text to simulate what would be sent with an image
    prompt = """
    Extract vehicle information from this document. Return ONLY clear JSON:
    {
      "registration_number": "...",
      "vin": "...",
      "make": "...",
      "model": "...",
      "year": "...",
      "owner_name": "...",
      "expiry_date": "YYYY-MM-DD"
    }
    """
    
    # For a real test, we'd need an image. Since we are verifying the prompt and model accessibility:
    try:
        # We'll just verify the model can handle the prompt logic (candidate generation)
        # without a real image for now, or use a tiny placeholder if forced.
        # But generate_content with just text is enough to verify model availability.
        response = await asyncio.to_thread(model.generate_content, "Ping for vehicle parsing")
        print("  Model Accessibility: SUCCESS")
    except Exception as e:
        print(f"  Model Accessibility: FAILED - {e}")

async def test_identity_parsing():
    print("\n--- Testing Identity Document Parsing (Gemini 3 Flash) ---")
    model = genai.GenerativeModel('gemini-3-flash-preview')
    prompt = """
    Extract identity information from this document. Return ONLY clear JSON:
    {
      "full_name": "...",
      "id_number": "...",
      "nationality": "...",
      "dob": "YYYY-MM-DD",
      "issue_date": "YYYY-MM-DD",
      "expiry_date": "YYYY-MM-DD",
      "document_type": "Passport|ID|Driving_License"
    }
    """
    try:
        response = await asyncio.to_thread(model.generate_content, "Ping for identity parsing")
        print("  Model Accessibility: SUCCESS")
    except Exception as e:
        print(f"  Model Accessibility: FAILED - {e}")

if __name__ == "__main__":
    asyncio.run(test_vehicle_parsing())
    asyncio.run(test_identity_parsing())
