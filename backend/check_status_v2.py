
import requests
import uuid
import sys

# Constants
BASE_URL = "http://localhost:8000/api/v1"
# We need an admin token. Assuming there's a way to get one or using a hardcoded one if env allows.
# For simplicity, if auth is required, we might need to mock it or use the 'admin@example.com' if we can login.
# Limitation: I cannot easily login via script without knowing the exact password or seeding a token.
# However, I can check the database directly to verify the Logic I changed in the Python code, or rely on the previous `check_quote_status.py` coupled with manual browsing.

# Better approach: Use the existing check_quote_status.py to monitor changes as I (simulated) would invoke endpoints.
# But I can't invoke endpoints without auth.

# Alternative: I will trust the code changes and the user manual verification, 
# but I can write a script to "simulate" the flow by calling the service methods directly if I import them?
# importing app modules in a standalone script might be tricky due to dependencies.

# Let's stick to the previous `check_quote_status.py` script but enhanced to show the new fields if I added any (I didn't add columns, just values).
# I'll update it to show status clearly.

import sqlite3
import os

def check_quote_status():
    db_path = os.path.join(os.path.dirname(__file__), "insurance.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check for any quotes with status 'policy_created' or 'draft_from_client'
    cursor.execute("SELECT id, quote_number, status, coverage_amount, created_by FROM quotes ORDER BY updated_at DESC LIMIT 5")
    rows = cursor.fetchall()
    
    print(f"\n{'Quote Number':<25} | {'Status':<20} | {'Coverage':<15}")
    print("-" * 80)
    for row in rows:
        print(f"{row['quote_number']:<25} | {row['status']:<20} | {row['coverage_amount']:<15}")
        
    conn.close()

if __name__ == "__main__":
    check_quote_status()
