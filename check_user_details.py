import sqlite3
import sys
import uuid

def check_user(email):
    # Try to find the DB. Settings say backend/insurance.db?
    # Actually let's just find it.
    db_path = 'backend/insurance.db'
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, company_id, email, user_type FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        if user:
            uid, cid, email, role = user
            print(f"User Email: {email}")
            print(f"User ID: {uid}")
            print(f"Company ID: {cid} (Type: {type(cid)})")
            print(f"Role: {role}")
            
            if cid:
                cursor.execute("SELECT name FROM companies WHERE id=?", (cid,))
                company = cursor.fetchone()
                if company:
                    print(f"Company Name: {company[0]}")
                else:
                    print("Company ID exists but NO record found in companies table!")
        else:
            print(f"User {email} not found")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_user(sys.argv[1])
    else:
        print("Usage: python check_user_details.py <email>")
