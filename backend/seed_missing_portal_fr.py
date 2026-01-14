from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.translation import Translation

def seed_missing_translations():
    db = SessionLocal()
    
    missing_translations = [
        {"key": "portal.policy_label", "value": "Police :", "group": "portal"},
        {"key": "portal.check_details", "value": "Veuillez vérifier que les détails dans la section 'Votre couverture' et vos documents sont exacts et répondent toujours à vos besoins.", "group": "portal"},
        {"key": "portal.prev_policy", "value": "Police précédente", "group": "portal"},
        {"key": "portal.renewal_date", "value": "Date de renouvellement :", "group": "portal"},
        {"key": "portal.next_policy", "value": "Police suivante", "group": "portal"},
        {"key": "portal.renewal_notice", "value": "Au moment du renouvellement, vous pourrez le consulter sur cette page.", "group": "portal"},
        {"key": "portal.your_cover", "value": "Votre Couverture d'Assurance", "group": "portal"},
        {"key": "portal.manage_policy", "value": "Gérez les détails de votre police, vos documents et vos renouvellements au même endroit.", "group": "portal"},
        {"key": "portal.tab_summary", "value": "Résumé de police", "group": "portal"},
        {"key": "portal.tab_docs", "value": "Voir documents", "group": "portal"},
        {"key": "portal.tab_upload", "value": "Téléverser documents", "group": "portal"},
        {"key": "portal.tab_payment", "value": "Paiement", "group": "portal"},
        {"key": "portal.overview_title", "value": "Vue d'ensemble de votre police", "group": "portal"},
        {"key": "portal.policy_num", "value": "Numéro de police :", "group": "portal"},
        {"key": "portal.cover_level", "value": "Niveau de couverture :", "group": "portal"},
        {"key": "portal.start_date", "value": "Date de début :", "group": "portal"},
        {"key": "portal.underwritten_by", "value": "Souscrit par :", "group": "portal"},
        {"key": "portal.ncd", "value": "Bonus (NCD) :", "group": "portal"},
        {"key": "portal.ncd_protected", "value": "Bonus protégé :", "group": "portal"},
        {"key": "portal.vehicle", "value": "Véhicule", "group": "portal"},
        {"key": "portal.cover_use", "value": "Couverture et usage", "group": "portal"},
        {"key": "portal.policy_type_label", "value": "Type de Police", "group": "portal"},
        {"key": "portal.extras", "value": "Options supplémentaires", "group": "portal"},
        {"key": "portal.no_extras", "value": "Aucune option achetée", "group": "portal"},
        {"key": "portal.excesses", "value": "Franchises", "group": "portal"},
        {"key": "portal.voluntary", "value": "Volontaire :", "group": "portal"},
        {"key": "portal.compulsory", "value": "Obligatoire :", "group": "portal"},
        {"key": "portal.view_excesses", "value": "Voir toutes les franchises", "group": "portal"},
        {"key": "portal.drivers", "value": "Conducteurs", "group": "portal"},
        {"key": "portal.manage_drivers", "value": "Gérer les conducteurs", "group": "portal"},
        {"key": "portal.claims", "value": "Sinistres", "group": "portal"},
        {"key": "portal.no_claims", "value": "Aucun sinistre ou condamnation au cours des 5 dernières années", "group": "portal"},
        {"key": "portal.my_docs", "value": "Mes Documents", "group": "portal"},
        {"key": "portal.shared_docs", "value": "Partagés avec moi", "group": "portal"},
        {"key": "portal.public_dataset", "value": "Données Publiques", "group": "portal"},
        {"key": "portal.referrals", "value": "Parrainages", "group": "portal"},
        {"key": "portal.settlements", "value": "Règlements Réseau", "group": "portal"},
        {"key": "portal.my_docs_title", "value": "Mes Documents", "group": "portal"},
        {"key": "portal.my_docs_desc", "value": "Gérez les fichiers que vous possédez. Configurez les permissions de partage.", "group": "portal"},
        {"key": "portal.empty_cat", "value": "Catégorie vide :", "group": "portal"},
        {"key": "portal.select_tab", "value": "Essayez de sélectionner un autre onglet pour voir vos éléments.", "group": "portal"},
        {"key": "portal.drag_upload", "value": "Cliquez ou glissez des fichiers ici", "group": "portal"},
        {"key": "portal.upload_support", "value": "Support pour PDF, JPG, PNG jusqu'à 10Mo", "group": "portal"},
        {"key": "portal.browse_files", "value": "Parcourir", "group": "portal"},
        {"key": "common.your", "value": "Votre", "group": "common"},
        {"key": "common.cover", "value": "Couverture", "group": "common"},
        {"key": "common.years", "value": "ans", "group": "common"},
        {"key": "common.yes", "value": "Oui", "group": "common"},
        {"key": "common.no", "value": "Non", "group": "common"},
        {"key": "common.share", "value": "Partager", "group": "common"},
    ]
    
    print(f"Checking {len(missing_translations)} keys...")
    
    added_count = 0
    skipped_count = 0 
    
    for t_data in missing_translations:
        # Check if exists
        exists = db.query(Translation).filter(
            Translation.key == t_data["key"],
            Translation.language_code == "fr"
        ).first()
        
        if not exists:
            new_trans = Translation(
                key=t_data["key"],
                value=t_data["value"],
                language_code="fr",
                group=t_data["group"],
                is_active=True
            )
            db.add(new_trans)
            added_count += 1
            print(f"Added: {t_data['key']}")
        else:
            skipped_count += 1
            
    db.commit()
    print(f"Finished. Added: {added_count}, Skipped: {skipped_count}")
    db.close()

if __name__ == "__main__":
    seed_missing_translations()
