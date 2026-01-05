
import sqlite3
import uuid

DB_PATH = "./insurance.db"
POLICY_TYPE_ID = "504a80d6-ec5d-464c-a7ea-89798861878d" # 'Silver Commuter' from verifying output
# Or I should find ALL policies and link services to them for robustness?
# Let's link to ALL premium policy types to be safe.

def seed_services():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Checking Policy Types...")
    cursor.execute("SELECT id, name, company_id FROM premium_policy_types")
    policies = cursor.fetchall()
    if not policies:
        print("No premium policy types found to seed!")
        return

    # Define standard services
    services_to_add = [
        ("Windscreen Cover", "Repairs or replaces damaged windscreen"),
        ("Courtesy Car", "Temporary car while yours is being repaired"),
        ("Breakdown Cover", "Roadside assistance"),
        ("Personal Accident Cover", "Compensation for serious injury")
    ]
    
    service_ids = []
    
    print("Ensuring Services exist...")
    # Find company ID from first policy
    company_id = policies[0][2] 
    
    for name, desc in services_to_add:
        # Check if exists
        cursor.execute("SELECT id FROM policy_services WHERE name_en = ?", (name,))
        row = cursor.fetchone()
        if row:
            s_id = row[0]
        else:
            s_id = str(uuid.uuid4())
            print(f"Creating Service: {name}")
            cursor.execute("""
                INSERT INTO policy_services (id, company_id, name_en, description, default_price, is_active)
                VALUES (?, ?, ?, ?, 0, 1)
            """, (s_id, company_id, name, desc))
        service_ids.append(s_id)
    
    print("Linking Services to Policies...")
    for pid, pname, cid in policies:
        print(f"Linking to {pname}...")
        for sid in service_ids:
            # Check linkage
            cursor.execute("""
                SELECT 1 FROM premium_policy_service_association 
                WHERE policy_type_id = ? AND service_id = ?
            """, (pid, sid))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO premium_policy_service_association (policy_type_id, service_id)
                    VALUES (?, ?)
                """, (pid, sid))
                print(f"  Linked {sid} to {pid}")
    
    conn.commit()
    conn.close()
    print("Seeding Complete.")

if __name__ == "__main__":
    seed_services()
