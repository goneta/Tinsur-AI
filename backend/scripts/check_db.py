
import sys
import os
import psycopg2
from psycopg2 import OperationalError

# Standard dev credentials
DB_NAME = "insurance_saas"
DB_USER = "postgres"
DB_PASS = "password"
DB_HOST = "localhost"
DB_PORT = "5432"

def create_connection():
    connection = None
    try:
        connection = psycopg2.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT,
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection

if __name__ == "__main__":
    conn = create_connection()
    if conn:
        conn.close()
        sys.exit(0)
    else:
        sys.exit(1)
