#!/usr/bin/env python
"""Run Tinsur-AI server with error handling"""

import sys
import os

# Set up path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Step 1: Loading environment...")
try:
    from dotenv import load_dotenv
    backend_root = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_root)
    load_dotenv(os.path.join(backend_root, ".env"))
    load_dotenv(os.path.join(project_root, ".env"))
    print("  OK - Environment loaded")
except Exception as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

print("\nStep 2: Loading app...")
try:
    from app.main import app
    print("  OK - App loaded")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 3: Running Uvicorn server...")
try:
    import uvicorn
    print("  Starting server on 0.0.0.0:8000...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False,
    )
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
