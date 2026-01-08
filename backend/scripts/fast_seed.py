import requests
import json

API_URL = "http://localhost:8000/api/v1/translations/"

new_translations = [
    # Claim Details - English
    {"key": "claim_details.title", "language_code": "en", "value": "Claim Details", "group": "claim_details"},
    {"key": "claim_details.submitted_date_static", "language_code": "en", "value": "Submitted on January 5th, 2026", "group": "claim_details"},
    {"key": "claim_details.incident_date", "language_code": "en", "value": "Incident Date", "group": "claim_details"},
    {"key": "claim_details.incident_date_static", "language_code": "en", "value": "March 11th, 2026", "group": "claim_details"},
    {"key": "claim_details.claim_amount", "language_code": "en", "value": "Claim Amount", "group": "claim_details"},
    {"key": "claim_details.amount_static", "language_code": "en", "value": "190 830 F CFA", "group": "claim_details"},
    {"key": "claim_details.description", "language_code": "en", "value": "Description", "group": "claim_details"},
    {"key": "claim_details.desc_lorem", "language_code": "en", "value": "Our ready Republican. Seat rate someone how.", "group": "claim_details"},
    {"key": "claim_details.location", "language_code": "en", "value": "Location", "group": "claim_details"},
    {"key": "claim_details.location_static", "language_code": "en", "value": "Alejandroside", "group": "claim_details"},
    {"key": "claim_details.ai_assessment", "language_code": "en", "value": "AI Damage Assessment", "group": "claim_details"},
    {"key": "claim_details.upload_photos_desc", "language_code": "en", "value": "Upload photos to enable AI damage assessment.", "group": "claim_details"},
    {"key": "claim_details.run_ai_review", "language_code": "en", "value": "Run AI Review", "group": "claim_details"},
    {"key": "claim_details.fraud_review", "language_code": "en", "value": "Fraud & Risk Review", "group": "claim_details"},
    {"key": "claim_details.fraud_scan_desc", "language_code": "en", "value": "Fraud scan will run automatically during AI damage assessment.", "group": "claim_details"},
    {"key": "claim_details.force_rescan", "language_code": "en", "value": "Force Re-scan", "group": "claim_details"},
    {"key": "claim_details.close", "language_code": "en", "value": "Close", "group": "claim_details"},
    {"key": "claim_details.paid", "language_code": "en", "value": "Paid", "group": "claim_details"},

    # Claim Details - French
    {"key": "claim_details.title", "language_code": "fr", "value": "Détails de la réclamation", "group": "claim_details"},
    {"key": "claim_details.submitted_date_static", "language_code": "fr", "value": "Soumis le 5 janvier 2026", "group": "claim_details"},
    {"key": "claim_details.incident_date", "language_code": "fr", "value": "Date de l'incident", "group": "claim_details"},
    {"key": "claim_details.incident_date_static", "language_code": "fr", "value": "11 mars 2026", "group": "claim_details"},
    {"key": "claim_details.claim_amount", "language_code": "fr", "value": "Montant de la réclamation", "group": "claim_details"},
    {"key": "claim_details.amount_static", "language_code": "fr", "value": "190 830 F CFA", "group": "claim_details"},
    {"key": "claim_details.description", "language_code": "fr", "value": "Description", "group": "claim_details"},
    {"key": "claim_details.desc_lorem", "language_code": "fr", "value": "Notre prêt Républicain. Taux de siège quelqu'un comment.", "group": "claim_details"},
    {"key": "claim_details.location", "language_code": "fr", "value": "Emplacement", "group": "claim_details"},
    {"key": "claim_details.location_static", "language_code": "fr", "value": "Alejandroside", "group": "claim_details"},
    {"key": "claim_details.ai_assessment", "language_code": "fr", "value": "Évaluation des dommages par IA", "group": "claim_details"},
    {"key": "claim_details.upload_photos_desc", "language_code": "fr", "value": "Téléchargez des photos pour activer l'évaluation des dommages par IA.", "group": "claim_details"},
    {"key": "claim_details.run_ai_review", "language_code": "fr", "value": "Exécuter l'examen IA", "group": "claim_details"},
    {"key": "claim_details.fraud_review", "language_code": "fr", "value": "Examen des fraudes et des risques", "group": "claim_details"},
    {"key": "claim_details.fraud_scan_desc", "language_code": "fr", "value": "L'analyse de fraude s'exécutera automatiquement lors de l'évaluation des dommages par IA.", "group": "claim_details"},
    {"key": "claim_details.force_rescan", "language_code": "fr", "value": "Forcer une nouvelle analyse", "group": "claim_details"},
    {"key": "claim_details.close", "language_code": "fr", "value": "Fermer", "group": "claim_details"},
    {"key": "claim_details.paid", "language_code": "fr", "value": "Payé", "group": "claim_details"},
    
    # Create New Client - English
    {"key": "create_new_client.title", "language_code": "en", "value": "Create New Client", "group": "create_new_client"},
    {"key": "create_new_client.subtitle", "language_code": "en", "value": "Add a new client to your system. Full insurance details can be added after creation.", "group": "create_new_client"},
    {"key": "create_new_client.ai_verification", "language_code": "en", "value": "AI Verification & Auto-fill", "group": "create_new_client"},
    {"key": "create_new_client.upload_desc", "language_code": "en", "value": "Upload a photo of the document to automatically extract and verify information.", "group": "create_new_client"},
    {"key": "create_new_client.scan_identity", "language_code": "en", "value": "Scan Identity/DL", "group": "create_new_client"},
    {"key": "create_new_client.scan_car_papers", "language_code": "en", "value": "Scan Car Papers", "group": "create_new_client"},
    {"key": "create_new_client.client_type", "language_code": "en", "value": "Client Type", "group": "create_new_client"},
    {"key": "create_new_client.individual", "language_code": "en", "value": "Individual", "group": "create_new_client"},
    {"key": "create_new_client.first_name", "language_code": "en", "value": "First Name", "group": "create_new_client"},
    {"key": "create_new_client.last_name", "language_code": "en", "value": "Last Name", "group": "create_new_client"},
    {"key": "create_new_client.email", "language_code": "en", "value": "Email", "group": "create_new_client"},
    {"key": "create_new_client.phone", "language_code": "en", "value": "Phone", "group": "create_new_client"},
    {"key": "create_new_client.kyc_status", "language_code": "en", "value": "KYC Status", "group": "create_new_client"},
    {"key": "create_new_client.pending", "language_code": "en", "value": "Pending", "group": "create_new_client"},
    {"key": "create_new_client.nationality", "language_code": "en", "value": "Nationality", "group": "create_new_client"},
    {"key": "create_new_client.nationality_ivorian", "language_code": "en", "value": "Ivorian", "group": "create_new_client"},
    {"key": "create_new_client.occupation", "language_code": "en", "value": "Occupation", "group": "create_new_client"},
    {"key": "create_new_client.account_manager", "language_code": "en", "value": "Account Manager (Created By)", "group": "create_new_client"},
    {"key": "create_new_client.select_employee", "language_code": "en", "value": "Select Employee", "group": "create_new_client"},
    {"key": "create_new_client.address", "language_code": "en", "value": "Address", "group": "create_new_client"},
    {"key": "create_new_client.city", "language_code": "en", "value": "City", "group": "create_new_client"},
    {"key": "create_new_client.country", "language_code": "en", "value": "Country", "group": "create_new_client"},
    {"key": "create_new_client.country_ci", "language_code": "en", "value": "Côte d'Ivoire", "group": "create_new_client"},
    {"key": "create_new_client.employment_status", "language_code": "en", "value": "Employment Status", "group": "create_new_client"},
    {"key": "create_new_client.employed", "language_code": "en", "value": "Employed", "group": "create_new_client"},
    {"key": "create_new_client.dl_duration", "language_code": "en", "value": "Driving License Duration (Years)", "group": "create_new_client"},
    {"key": "create_new_client.num_accidents", "language_code": "en", "value": "Number of Accidents", "group": "create_new_client"},
    {"key": "create_new_client.ncb", "language_code": "en", "value": "No-Claims Bonus (Years)", "group": "create_new_client"},
    {"key": "create_new_client.cancel", "language_code": "en", "value": "Cancel", "group": "create_new_client"},
    {"key": "create_new_client.submit", "language_code": "en", "value": "Create Client", "group": "create_new_client"},

    # Create New Client - French
    {"key": "create_new_client.title", "language_code": "fr", "value": "Créer un nouveau client", "group": "create_new_client"},
    {"key": "create_new_client.subtitle", "language_code": "fr", "value": "Ajoutez un nouveau client à votre système. Les détails complets de l'assurance peuvent être ajoutés après la création.", "group": "create_new_client"},
    {"key": "create_new_client.ai_verification", "language_code": "fr", "value": "Vérification IA et remplissage automatique", "group": "create_new_client"},
    {"key": "create_new_client.upload_desc", "language_code": "fr", "value": "Téléchargez une photo du document pour extraire et vérifier automatiquement les informations.", "group": "create_new_client"},
    {"key": "create_new_client.scan_identity", "language_code": "fr", "value": "Scanner identité/permis", "group": "create_new_client"},
    {"key": "create_new_client.scan_car_papers", "language_code": "fr", "value": "Scanner papiers de voiture", "group": "create_new_client"},
    {"key": "create_new_client.client_type", "language_code": "fr", "value": "Type de client", "group": "create_new_client"},
    {"key": "create_new_client.individual", "language_code": "fr", "value": "Individuel", "group": "create_new_client"},
    {"key": "create_new_client.first_name", "language_code": "fr", "value": "Prénom", "group": "create_new_client"},
    {"key": "create_new_client.last_name", "language_code": "fr", "value": "Nom de famille", "group": "create_new_client"},
    {"key": "create_new_client.email", "language_code": "fr", "value": "E-mail", "group": "create_new_client"},
    {"key": "create_new_client.phone", "language_code": "fr", "value": "Téléphone", "group": "create_new_client"},
    {"key": "create_new_client.kyc_status", "language_code": "fr", "value": "Statut KYC", "group": "create_new_client"},
    {"key": "create_new_client.pending", "language_code": "fr", "value": "En attente", "group": "create_new_client"},
    {"key": "create_new_client.nationality", "language_code": "fr", "value": "Nationalité", "group": "create_new_client"},
    {"key": "create_new_client.nationality_ivorian", "language_code": "fr", "value": "Ivoirien", "group": "create_new_client"},
    {"key": "create_new_client.occupation", "language_code": "fr", "value": "Profession", "group": "create_new_client"},
    {"key": "create_new_client.account_manager", "language_code": "fr", "value": "Gestionnaire de compte (Créé par)", "group": "create_new_client"},
    {"key": "create_new_client.select_employee", "language_code": "fr", "value": "Sélectionner un employé", "group": "create_new_client"},
    {"key": "create_new_client.address", "language_code": "fr", "value": "Adresse", "group": "create_new_client"},
    {"key": "create_new_client.city", "language_code": "fr", "value": "Ville", "group": "create_new_client"},
    {"key": "create_new_client.country", "language_code": "fr", "value": "Pays", "group": "create_new_client"},
    {"key": "create_new_client.country_ci", "language_code": "fr", "value": "Côte d'Ivoire", "group": "create_new_client"},
    {"key": "create_new_client.employment_status", "language_code": "fr", "value": "Statut d'emploi", "group": "create_new_client"},
    {"key": "create_new_client.employed", "language_code": "fr", "value": "Employé", "group": "create_new_client"},
    {"key": "create_new_client.dl_duration", "language_code": "fr", "value": "Durée du permis de conduire (Années)", "group": "create_new_client"},
    {"key": "create_new_client.num_accidents", "language_code": "fr", "value": "Nombre d'accidents", "group": "create_new_client"},
    {"key": "create_new_client.ncb", "language_code": "fr", "value": "Bonus sans sinistre (Années)", "group": "create_new_client"},
    {"key": "create_new_client.cancel", "language_code": "fr", "value": "Annuler", "group": "create_new_client"},
    {"key": "create_new_client.submit", "language_code": "fr", "value": "Créer un client", "group": "create_new_client"},

    # Collaboration Hub - English
    {"key": "collaboration_hub.title", "language_code": "en", "value": "Collaboration Hub", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.description", "language_code": "en", "value": "Securely share and access resources across the network.", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.upload_share", "language_code": "en", "value": "Upload & Share", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.my_documents", "language_code": "en", "value": "My Documents", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.shared_with_me", "language_code": "en", "value": "Shared with Me", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.public_dataset", "language_code": "en", "value": "Public Dataset", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.referrals", "language_code": "en", "value": "Referrals", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.network_settlements", "language_code": "en", "value": "Network Settlements", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.my_docs_desc", "language_code": "en", "value": "Manage files you own. Configure sharing permissions.", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.file_job_anyone", "language_code": "en", "value": "job_anyone.pdf", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.car_papers", "language_code": "en", "value": "Car Papers", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.size_2_28", "language_code": "en", "value": "2.28 MB", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.date_2026_01_05", "language_code": "en", "value": "2026-01-05", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.public", "language_code": "en", "value": "PUBLIC", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.share", "language_code": "en", "value": "Share", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.file_marriage_score", "language_code": "en", "value": "marriage_score.pdf", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.photo", "language_code": "en", "value": "Photo", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.size_2_44", "language_code": "en", "value": "2.44 MB", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.private", "language_code": "en", "value": "PRIVATE", "group": "collaboration_hub_documents"},

    # Collaboration Hub - French
    {"key": "collaboration_hub.title", "language_code": "fr", "value": "Centre de collaboration", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.description", "language_code": "fr", "value": "Partagez et accédez en toute sécurité aux ressources sur l'ensemble du réseau.", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.upload_share", "language_code": "fr", "value": "Télécharger et partager", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.my_documents", "language_code": "fr", "value": "Mes documents", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.shared_with_me", "language_code": "fr", "value": "Partagé avec moi", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.public_dataset", "language_code": "fr", "value": "Ensemble de données public", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.referrals", "language_code": "fr", "value": "Références", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.network_settlements", "language_code": "fr", "value": "Règlements de réseau", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.my_docs_desc", "language_code": "fr", "value": "Gérez les fichiers que vous possédez. Configurez les autorisations de partage.", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.file_job_anyone", "language_code": "fr", "value": "job_anyone.pdf", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.car_papers", "language_code": "fr", "value": "Papiers de voiture", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.size_2_28", "language_code": "fr", "value": "2,28 Mo", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.date_2026_01_05", "language_code": "fr", "value": "2026-01-05", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.public", "language_code": "fr", "value": "PUBLIC", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.share", "language_code": "fr", "value": "Partager", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.file_marriage_score", "language_code": "fr", "value": "marriage_score.pdf", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.photo", "language_code": "fr", "value": "Photo", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.size_2_44", "language_code": "fr", "value": "2,44 Mo", "group": "collaboration_hub_documents"},
    {"key": "collaboration_hub.private", "language_code": "fr", "value": "PRIVÉ", "group": "collaboration_hub_documents"},
]

def seed_fast():
    print(f"Fast seeding {len(new_translations)} keys...")
    for item in new_translations:
        try:
            # Check exist first to be safe, or just use create which might fail if exists
            # We can use create and ignore errors
            resp = requests.post(API_URL, json=item)
            if resp.status_code in [200, 201]:
                print(f"Created: {item['key']} ({item['language_code']})")
            elif resp.status_code == 400 and "already exists" in resp.text:
                print(f"Skipped (Exists): {item['key']} ({item['language_code']})")
            else:
                print(f"Error {resp.status_code} for {item['key']}: {resp.text}")
        except Exception as e:
            print(f"Exception for {item['key']}: {e}")

if __name__ == "__main__":
    seed_fast()
