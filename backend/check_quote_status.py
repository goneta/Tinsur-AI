
import sys
import os
import sqlite3

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_latest_quote_status():
    db_path = os.path.join(os.path.dirname(__file__), "insurance.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, quote_number, status, coverage_amount, created_by FROM quotes ORDER BY created_at DESC LIMIT 5")
    rows = cursor.fetchall()
    
    print(f"{'Quote Number':<25} | {'Status':<15} | {'Coverage':<15} | {'Created By'}")
    print("-" * 80)
    for row in rows:
        print(f"{row['quote_number']:<25} | {row['status']:<15} | {row['coverage_amount']:<15} | {row['created_by']}")
        
    conn.close()

if __name__ == "__main__":
    check_latest_quote_status()
