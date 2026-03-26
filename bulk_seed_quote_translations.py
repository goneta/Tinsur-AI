import sqlite3
import os

translations = [
    # Quote Wizard - English
    {"key": "quote.wizard.step1_title", "language_code": "en", "value": "Create New Quote - Step 1 of 3", "group": "quote"},
    {"key": "quote.wizard.find_client", "language_code": "en", "value": "Find a Client", "group": "quote"},
    {"key": "quote.wizard.search_client_placeholder", "language_code": "en", "value": "Search by name or email...", "group": "quote"},
    {"key": "quote.wizard.no_clients", "language_code": "en", "value": "No clients found.", "group": "quote"},
    {"key": "quote.wizard.select", "language_code": "en", "value": "Select", "group": "quote"},
    
    # Quote Wizard - French
    {"key": "quote.wizard.step1_title", "language_code": "fr", "value": "Créer un nouveau devis - Étape 1 sur 3", "group": "quote"},
    {"key": "quote.wizard.find_client", "language_code": "fr", "value": "Trouver un client", "group": "quote"},
    {"key": "quote.wizard.search_client_placeholder", "language_code": "fr", "value": "Rechercher par nom ou email...", "group": "quote"},
    {"key": "quote.wizard.no_clients", "language_code": "fr", "value": "Aucun client trouvé.", "group": "quote"},
    {"key": "quote.wizard.select", "language_code": "fr", "value": "Sélectionner", "group": "quote"},
]

db_path = 'backend/insurance.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Bulk seeding critical translations...")
for t in translations:
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO translations (id, key, language_code, value, [group], created_at, updated_at) VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
            (f"{t['key']}_{t['language_code']}", t['key'], t['language_code'], t['value'], t['group'])
        )
    except Exception as e:
        print(f"Error for {t['key']}: {e}")

conn.commit()
conn.close()
print("Done.")
