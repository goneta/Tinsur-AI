import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import engine
from sqlalchemy import text

print(f"Testing connection with: {engine.url}")

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"Connection successful: {result.scalar()}")
        
    print("Testing create_all...")
    from app.core.database import Base
    Base.metadata.create_all(bind=engine)
    print("create_all successful")
    
except Exception as e:
    print(f"Connection failed: {e}")
    # Print full traceback
    import traceback
    traceback.print_exc()
