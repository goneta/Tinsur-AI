import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.main import app

def print_routes():
    print("Registered Routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"{route.methods} {route.path}")
        elif hasattr(route, 'path_format'):
             print(f"{route.methods} {route.path_format}")

if __name__ == "__main__":
    print_routes()
