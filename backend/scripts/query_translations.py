import requests

print("Querying translations API...")
try:
    r = requests.get('http://localhost:8000/api/v1/translations/keys/all')
    if r.status_code == 200:
        translations = r.json()
        print(f"Total translations found: {len(translations)}")
        for t in translations:
            print(f" - {t['key']} ({t['language_code']}): {t['value']}")
    else:
        print(f"Error: {r.status_code} - {r.text}")
except Exception as e:
    print(f"Failed: {e}")
