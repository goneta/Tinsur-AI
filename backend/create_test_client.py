import sys
import os
from sqlalchemy import text
from app.core.database import engine
from app.core.security import get_password_hash
import uuid
import datetime

def create_test_client_raw():
    try:
        with engine.connect() as connection:
            # 1. Get a company ID
            result = connection.execute(text("SELECT id FROM companies LIMIT 1"))
            company_row = result.fetchone()
            if not company_row:
                print("Error: No company found in database.")
                return
            company_id = company_row[0]
            print(f"Using Company ID: {company_id}")

            email = "test_client@tinsur.ai"
            password = "password123"
            hashed_password = get_password_hash(password)
            
            # 2. Check if user exists
            result = connection.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email})
            user_row = result.fetchone()
            
            if user_row:
                user_id = user_row[0]
                print(f"User {email} already exists with ID: {user_id}")
            else:
                # 3. Create User
                user_id = str(uuid.uuid4())
                print(f"Creating user {email}...")
                now = datetime.datetime.utcnow().isoformat()
                
                # Check for pos_location_id column existence or just use NULL if nullable
                # Assuming standard columns from models.py
                
                insert_user = text("""
                    INSERT INTO users (id, company_id, email, password_hash, first_name, last_name, role, is_active, is_verified, created_at, updated_at)
                    VALUES (:id, :company_id, :email, :password_hash, 'Test', 'Client', 'client', 1, 1, :now, :now)
                """)
                connection.execute(insert_user, {
                    "id": user_id,
                    "company_id": company_id,
                    "email": email,
                    "password_hash": hashed_password,
                    "now": now
                })
                connection.commit()
                print("User created.")

            # 4. Check if client profile exists
            result = connection.execute(text("SELECT id FROM clients WHERE user_id = :user_id"), {"user_id": user_id})
            client_row = result.fetchone()
            
            if client_row:
                print("Client profile already exists.")
            else:
                # 5. Create Client Profile
                client_id = str(uuid.uuid4())
                print("Creating client profile...")
                now = datetime.datetime.utcnow().isoformat()
                
                insert_client = text("""
                    INSERT INTO clients (id, company_id, user_id, client_type, first_name, last_name, email, status, created_at, updated_at)
                    VALUES (:id, :company_id, :user_id, 'individual', 'Test', 'Client', :email, 'active', :now, :now)
                """)
                connection.execute(insert_client, {
                    "id": client_id,
                    "company_id": company_id,
                    "user_id": user_id,
                    "email": email,
                    "now": now
                })
                connection.commit()
                print("Client profile created.")

            print("\n" + "="*50)
            print("CLIENT LOGIN CREDENTIALS")
            print("="*50)
            print(f"Email:    {email}")
            print(f"Password: {password}")
            print("="*50 + "\n")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_test_client_raw()
