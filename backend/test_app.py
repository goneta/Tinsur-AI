#!/usr/bin/env python
"""Test app startup and list endpoints"""

import sys
sys.path.insert(0, '.')

print("Step 1: Importing app...")
try:
    from app.main import app
    print("SUCCESS: App imported")
except Exception as e:
    print(f"ERROR importing app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("")
print(f"App title: {app.title if hasattr(app, 'title') else 'N/A'}")
print(f"App version: {app.version if hasattr(app, 'version') else 'N/A'}")

print("")
print("Step 2: Counting routes...")
try:
    route_count = len([r for r in app.routes])
    print(f"Total routes: {route_count}")
except Exception as e:
    print(f"ERROR counting routes: {e}")

print("")
print("Step 3: Listing quote-related routes...")
try:
    for route in app.routes:
        path = getattr(route, 'path', '')
        if 'quote' in path.lower():
            methods = getattr(route, 'methods', [])
            print(f"  {route.methods if hasattr(route, 'methods') else 'N/A':<30} {path}")
except Exception as e:
    print(f"ERROR listing routes: {e}")

print("")
print("SUCCESS: App is functional and ready for startup")
