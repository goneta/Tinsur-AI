
import sqlite3
import os

DB_PATH = "backend/insurance.db"

def add_column():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("Checking for system_registration_number column...")
        cursor.execute("PRAGMA table_info(companies)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "system_registration_number" in columns:
            print("Column 'system_registration_number' already exists.")
        else:
            print("Adding column 'system_registration_number'...")
            print("Adding column 'system_registration_number'...")
            cursor.execute("ALTER TABLE companies ADD COLUMN system_registration_number VARCHAR(50)")
            conn.commit()
            print("Column added. Creating unique index...")
            cursor.execute("CREATE UNIQUE INDEX ix_companies_system_registration_number ON companies (system_registration_number)")
            conn.commit()
            print("Index created successfully.")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_column()
