import sqlite3

conn = sqlite3.connect('insurance.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"Tables: {tables}")

for table in tables:
    tname = table[0]
    cursor.execute(f"PRAGMA table_info({tname});")
    columns = cursor.fetchall()
    print(f"Table {tname} columns: {[c[1] for c in columns]}")
