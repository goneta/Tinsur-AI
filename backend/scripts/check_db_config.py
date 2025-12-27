import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from app.core.config import settings
print(f"DATABASE_URL: {settings.DATABASE_URL}")
