import sqlite3

conn = sqlite3.connect('insurance.db')
cursor = conn.cursor()
cursor.execute("SELECT email, is_active FROM clients WHERE email = 'test_client@tinsur.ai'")
result = cursor.fetchone()
if result:
    print(f"Client found: {result}")
else:
    print("Client NOT found")
conn.close()
