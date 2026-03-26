#!/usr/bin/env python
import subprocess
import sys

print("=== TINSUR-AI BACKEND STARTUP ===")
print(f"Python: {sys.version}")
print(f"Working dir: {sys.path[0]}")
print("")

try:
    print("[1/3] Importing app...")
    from app.main import app
    print("[OK] App imported")
    
    print("[2/3] Checking routes...")
    route_count = len([r for r in app.routes])
    print(f"[OK] {route_count} routes found")
    
    print("[3/3] Starting server...")
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="debug",
        reload=False,
    )
except KeyboardInterrupt:
    print("\n[STOPPED] User interrupt")
except SystemExit as e:
    print(f"\n[EXIT] System exit code: {e.code}")
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
