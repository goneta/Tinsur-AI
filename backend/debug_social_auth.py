import traceback
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import social_auth...")
    from app.api.v1.endpoints import social_auth
    print("Import successful!")
except NameError as e:
    print(f"\nCAUGHT NAME ERROR: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"\nCAUGHT OTHER ERROR: {type(e).__name__}: {e}")
    traceback.print_exc()
