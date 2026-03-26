import os
from app.core.config import settings

def print_settings():
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    print(f"MONGODB_URL: {settings.MONGODB_URL}")
    print(f"REDIS_URL: {settings.REDIS_URL}")
    
    # Check actual env var
    print(f"ENV DATABASE_URL: {os.environ.get('DATABASE_URL')}")

if __name__ == "__main__":
    print_settings()
