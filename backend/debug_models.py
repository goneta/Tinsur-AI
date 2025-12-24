
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    from app.models.client import Client
    print("Client imported successfully")
    from app.models.client_details import ClientAutomobile
    print("ClientAutomobile imported successfully")
    from app.models import *
    print("All models imported successfully")
except Exception as e:
    print(f"Error importing models: {e}")
    import traceback
    traceback.print_exc()
