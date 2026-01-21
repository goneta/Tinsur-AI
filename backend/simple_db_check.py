import sqlite3
import os

db_path = 'backend/insurance.db'
email = 'johndoe_fix_verification@example.com'

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"Checking for {email}...")

# User
cursor.execute("SELECT id, email, user_type FROM users WHERE email=?", (email,))
user = cursor.fetchone()
if user:
    user_id = user[0]
    print(f"User found: ID={user_id}, Email={user[1]}, Type={user[2]}")
    
    # Client
    cursor.execute("SELECT id, first_name, last_name, client_type FROM clients WHERE user_id=?", (user_id,))
    client = cursor.fetchone()
    if client:
        client_id = client[0]
        print(f"Client found: ID={client_id}, Name={client[1]} {client[2]}, Type={client[3]}")
        
        # Drivers
        cursor.execute("SELECT id, first_name, last_name, is_main_driver, license_number FROM client_drivers WHERE client_id=?", (client_id,))
        drivers = cursor.fetchall()
        print(f"Drivers found: {len(drivers)}")
        for d in drivers:
            print(f"  - Driver: ID={d[0]}, Name={d[1]} {d[2]}, Main={d[3]}, License={d[4]}")
            
        # Automobiles
        cursor.execute("SELECT id, vehicle_make, vehicle_model, vehicle_registration FROM client_automobile WHERE client_id=?", (client_id,))
        autos = cursor.fetchall()
        print(f"Vehicles found: {len(autos)}")
        for a in autos:
            print(f"  - Vehicle: ID={a[0]}, Make={a[1]}, Model={a[2]}, Reg={a[3]}")
    else:
        print("Client record NOT found")
else:
    print("User record NOT found")

conn.close()
