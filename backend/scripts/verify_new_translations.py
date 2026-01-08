import requests

BASE_URL = "http://localhost:8000/api/v1/translations/keys/all"

keys_to_check = [
    "claim_details.title",
    "create_new_client.title",
    "collaboration_hub.title",
    "claim_details.submitted_date_static",
    "collaboration_hub.file_job_anyone"
]

def verify_keys():
    print("Verifying new keys...")
    all_present = True
    try:
        response = requests.get(BASE_URL)
        if response.status_code != 200:
            print(f"Failed to fetch translations: {response.status_code}")
            return

        translations = response.json()
        # Create a set of (key, lang) or just keys
        existing_keys = {t['key'] for t in translations}

        for key in keys_to_check:
            if key in existing_keys:
                print(f"[OK] Found key: {key}")
            else:
                print(f"[FAIL] Missing key: {key}")
                # Print similar keys
                similar = [k for k in existing_keys if key.split('.')[0] in k]
                print(f"    Found similar keys: {similar[:5]}...")
                all_present = False
        
        if all_present:
            print("\nSUCCESS: All sample new keys found in database.")
        else:
            print("\nFAILURE: Some keys are missing.")

    except Exception as e:
        print(f"Error verification: {e}")

if __name__ == "__main__":
    verify_keys()
