
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.translation import Translation

def seed_missing():
    db = SessionLocal()
    
    missing_translations = {
        "Payment": "Paiement",
        "Total Clients": "Total Clients",
        "Active Policies": "Polices Actives",
        "Pending Quotes": "Devis En Attente",
        "Monthly Revenue": "Revenu Mensuel",
        "Dashboard Overview": "Vue d'ensemble",
        "Recent Activity": "Activité Récente",
        "Quick Actions": "Actions Rapides",
        "Create New Quote": "Créer un Nouveau Devis",
        "Add New Client": "Ajouter un Client",
        "Process Payment": "Traiter le Paiement",
        "Download Report": "Télécharger le Rapport",
        "Welcome back! Here is your insurance portfolio summary.": "Bon retour ! Voici le résumé de votre portefeuille d'assurance.",
        "Your recent actions and notifications.": "Vos actions récentes et notifications.",
        "Frequently used actions.": "Actions fréquemment utilisées.",
        "No recent activity": "Aucune activité récente",
        "View all excesses": "Voir toutes les franchises",
        "Manage drivers": "Gérer les conducteurs",
        "No claims or convictions in last 5 years": "Aucun sinistre ou condamnation au cours des 5 dernières années",
        "My Documents": "Mes Documents",
        "Shared with me": "Partagé avec moi",
        "Public Dataset": "Jeu de données public",
        "Referrals": "Parrainages",
        "Network Settlements": "Règlements Réseau",
        "Click or drag files here": "Cliquez ou glissez des fichiers ici",
        "Support for PDF, JPG, PNG up to 10MB": "Support pour PDF, JPG, PNG jusqu'à 10 Mo",
        "Browse Files": "Parcourir les fichiers",
        "Share": "Partager",
        "Policy summary": "Résumé de la police",
        "View documents": "Voir les documents",
        "Upload documents": "Télécharger des documents",
        "Your policy overview": "Aperçu de votre police",
        "Policy number:": "Numéro de police:",
        "Cover level:": "Niveau de couverture:",
        "Start date:": "Date de début:",
        "Renewal date:": "Date de renouvellement:",
        "Underwritten by:": "Souscrit par:",
        "No Claims Discount:": "Bonus-Malus:",
        "NCD protected:": "Protection Bonus:",
        "years": "ans",
        "Yes": "Oui",
        "No": "Non",
        "Vehicle": "Véhicule",
        "Cover and use": "Couverture et usage",
        "Policy Type": "Type de Police",
        "Optional extras": "Options supplémentaires",
        "No optional extras purchased": "Aucune option supplémentaire achetée",
        "Excesses": "Franchises",
        "Voluntary:": "Volontaire:",
        "Compulsory:": "Obligatoire:",
        "Drivers": "Conducteurs",
        "Claims": "Sinistres",
        "from last month": "par rapport au mois dernier",
        "Please make sure the details in the 'Your Cover' section and your documents are accurate and still meet your needs.": "Veuillez vérifier que les détails de la section 'Votre couverture' et de vos documents sont exacts et répondent toujours à vos besoins.",
        "Previous policy": "Police précédente",
        "Next policy": "Police suivante",
        "When it's time for your renewal you'll be able to view it from this page.": "Au moment de votre renouvellement, vous pourrez le consulter sur cette page.",
        "Your": "Votre",
        "Cover": "Couverture",
        "Your Insurance Cover": "Votre Couverture d'Assurance",
        "Manage your policy details, documents, and renewals in one place.": "Gérez les détails de votre police, vos documents et vos renouvellements au même endroit."
    }
    
    count = 0
    for key, val_fr in missing_translations.items():
        # Upsert English
        existing_en = db.query(Translation).filter(
            Translation.key == key,
            Translation.language_code == "en"
        ).first()
        if not existing_en:
            db.add(Translation(key=key, language_code="en", value=key, group="ui"))
        
        # Upsert French
        existing_fr = db.query(Translation).filter(
            Translation.key == key,
            Translation.language_code == "fr"
        ).first()
        if not existing_fr:
            db.add(Translation(key=key, language_code="fr", value=val_fr, group="ui"))
            count += 1
        elif existing_fr.value != val_fr:
             existing_fr.value = val_fr
             
    db.commit()
    print(f"Added {count} missing translation keys.")
    db.close()

if __name__ == "__main__":
    seed_missing()
