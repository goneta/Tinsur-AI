import sqlite3

conn = sqlite3.connect('insurance.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM clients WHERE email = 'test_client@tinsur.ai'")
result = cursor.fetchone()
if result:
    print(f"Client found: {result}")
    # Print column names
    cursor.execute("PRAGMA table_info(clients)")
    cols = cursor.fetchall()
    print(f"Columns: {[c[1] for c in cols]}")
else:
    print("Client NOT found")
conn.close()
