
import os
import sys
from dotenv import load_dotenv

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

print(f"Current Working Directory: {os.getcwd()}")
print(f"Script Location: {os.path.abspath(__file__)}")

# Try to find .env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
print(f"Looking for .env at: {env_path}")
if os.path.exists(env_path):
    print("Found .env file!")
    load_dotenv(env_path)
else:
    print("WARNING: .env file NOT found!")

# Check Env Vars
db_url = os.getenv("DATABASE_URL")
if db_url:
    # Mask password
    masked = db_url.split("@")
    if len(masked) > 1:
        print(f"DATABASE_URL found: {masked[0].split(':')[0]}://****@{masked[1]}")
    else:
        print(f"DATABASE_URL found (unparseable format): {db_url[:10]}...")
else:
    print("ERROR: DATABASE_URL not set in environment!")

# Try Connection
if db_url:
    print("Attempting SQLAlchemy connection...")
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(db_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(f"Connection Successful! Result: {result.scalar()}")
    except Exception as e:
        print(f"Connection FAILED: {e}")
        import traceback
        traceback.print_exc()
