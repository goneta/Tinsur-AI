import psycopg2
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")

def test_db():
    url = os.getenv("DATABASE_URL")
    print(f"Testing connection to: {url}")
    try:
        conn = psycopg2.connect(url)
        print("Successfully connected to the database!")
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cur.fetchall()
        print(f"Tables found: {[t[0] for t in tables]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error connecting to the database: {e}")

if __name__ == "__main__":
    test_db()
