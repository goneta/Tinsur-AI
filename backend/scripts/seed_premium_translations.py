import requests

API_URL = "http://localhost:8000/api/v1/translations/"

new_translations = [
    {"key": "service.claims_concierge", "language_code": "en", "value": "Personal Claims Concierge", "group": "admin"},
    {"key": "service.priority_support", "language_code": "en", "value": "24/7 Priority Support", "group": "admin"},
    {"key": "service.replacement_vehicle_plus", "language_code": "en", "value": "Replacement Vehicle Plus", "group": "admin"},
    {"key": "service.premium_legal", "language_code": "en", "value": "Premium Legal Protection", "group": "admin"},
    
    {"key": "service.claims_concierge", "language_code": "fr", "value": "Concierge de sinistres personnel", "group": "admin"},
    {"key": "service.priority_support", "language_code": "fr", "value": "Assistance prioritaire 24/7", "group": "admin"},
    {"key": "service.replacement_vehicle_plus", "language_code": "fr", "value": "Véhicule de remplacement Plus", "group": "admin"},
    {"key": "service.premium_legal", "language_code": "fr", "value": "Protection juridique Premium", "group": "admin"},
]

def seed_new_translations():
    print("Seeding new premium translations...")
    for t in new_translations:
        try:
            response = requests.post(API_URL, json=t)
            if response.status_code == 201 or response.status_code == 200:
                print(f"Created: {t['key']} ({t['language_code']})")
            elif response.status_code == 400:
                print(f"Skipped (Exists): {t['key']} ({t['language_code']})")
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    seed_new_translations()
