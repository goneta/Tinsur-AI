import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app.core.config import settings
print(f"DATABASE_URL: {settings.DATABASE_URL}")
