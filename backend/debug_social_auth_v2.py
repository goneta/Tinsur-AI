import sys
import os
import traceback

# Add current directory to path
sys.path.append(os.getcwd())

try:
    print("Pre-import check: is FacebookLoginRequest in globals?", "FacebookLoginRequest" in globals())
    
    print("Importing FacebookLoginRequest from app.schemas.auth...")
    from app.schemas.auth import FacebookLoginRequest
    print("Post-import schema check: is FacebookLoginRequest in globals?", "FacebookLoginRequest" in globals())
    
    print("\nAttempting to import social_auth module...")
    from app.api.v1.endpoints import social_auth
    print("Social auth import successful!")
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    traceback.print_exc()
