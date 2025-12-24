import os
import google.generativeai as genai
from dotenv import load_dotenv
import traceback

def verify_key():
    load_dotenv(override=True)
    api_key = os.getenv("GOOGLE_API_KEY")
    print(f"DEBUG: Read key: '{api_key}'")
    
    if not api_key:
        print("Error: GOOGLE_API_KEY NOT FOUND.")
        return

    try:
        genai.configure(api_key=api_key)
        # Try a very basic call to list models to verify the key
        print("Attempting to list models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Found model: {m.name}")
        
        print("\nAttempting to generate content with gemini-2.0-flash...")
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content("Hello")
        print("--- SUCCESS ---")
        print(f"Response: {response.text}")
    except Exception as e:
        print("--- FAILED ---")
        print(f"Exception type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    verify_key()
