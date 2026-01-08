import requests
import json

# API Configuration
API_URL = "http://localhost:8000/api/v1/translations/"

# Missing translations to add
missing_translations = [
    # Common
    {"key": "common.done", "language_code": "en", "value": "Done", "group": "common"},
    {"key": "common.done", "language_code": "fr", "value": "Terminé", "group": "common"},
    
    # Claims
    {"key": "claims.open_menu", "language_code": "en", "value": "Open Menu", "group": "claims"},
    {"key": "claims.open_menu", "language_code": "fr", "value": "Ouvrir le menu", "group": "claims"},

    # Support
    {"key": "support.recent_tickets", "language_code": "en", "value": "Recent Tickets", "group": "support"},
    {"key": "support.recent_tickets", "language_code": "fr", "value": "Tickets récents", "group": "support"},

    # Telematics
    {"key": "telematics.driving_score", "language_code": "en", "value": "Driving Score", "group": "telematics"},
    {"key": "telematics.driving_score", "language_code": "fr", "value": "Score de conduite", "group": "telematics"},
    {"key": "telematics.trip_details", "language_code": "en", "value": "Trip Details", "group": "telematics"},
    {"key": "telematics.trip_details", "language_code": "fr", "value": "Détails du trajet", "group": "telematics"},

    # Financials
    {"key": "financials.title", "language_code": "en", "value": "Financial Dashboard", "group": "financials"},
    {"key": "financials.title", "language_code": "fr", "value": "Tableau de bord financier", "group": "financials"},
    {"key": "financials.desc", "language_code": "en", "value": "Financial overview and accounting", "group": "financials"},
    {"key": "financials.desc", "language_code": "fr", "value": "Aperçu financier et comptabilité", "group": "financials"},
    {"key": "financials.kpi_revenue", "language_code": "en", "value": "Total Revenue", "group": "financials"},
    {"key": "financials.kpi_revenue", "language_code": "fr", "value": "Revenu total", "group": "financials"},
    {"key": "financials.kpi_expenses", "language_code": "en", "value": "Total Expenses", "group": "financials"},
    {"key": "financials.kpi_expenses", "language_code": "fr", "value": "Dépenses totales", "group": "financials"},
    {"key": "financials.kpi_net_position", "language_code": "en", "value": "Net Position", "group": "financials"},
    {"key": "financials.kpi_net_position", "language_code": "fr", "value": "Position nette", "group": "financials"},
    {"key": "financials.reporting_standards", "language_code": "en", "value": "Reporting Standards", "group": "financials"},
    {"key": "financials.reporting_standards", "language_code": "fr", "value": "Normes de reporting", "group": "financials"},
    {"key": "financials.ifrs_pipeline", "language_code": "en", "value": "IFRS Pipeline", "group": "financials"},
    {"key": "financials.ifrs_pipeline", "language_code": "fr", "value": "Pipeline IFRS", "group": "financials"},
    {"key": "financials.reporting_range", "language_code": "en", "value": "Reporting Range", "group": "financials"},
    {"key": "financials.reporting_range", "language_code": "fr", "value": "Période de reporting", "group": "financials"},
    {"key": "financials.refresh", "language_code": "en", "value": "Refresh Data", "group": "financials"},
    {"key": "financials.refresh", "language_code": "fr", "value": "Actualiser les données", "group": "financials"},
    {"key": "financials.solvency_pulse", "language_code": "en", "value": "Solvency Pulse", "group": "financials"},
    {"key": "financials.solvency_pulse", "language_code": "fr", "value": "Impulsion de solvabilité", "group": "financials"},
    {"key": "financials.context_transactions", "language_code": "en", "value": "Recent Transactions", "group": "financials"},
    {"key": "financials.context_transactions", "language_code": "fr", "value": "Transactions récentes", "group": "financials"},
    {"key": "financials.trans_ref", "language_code": "en", "value": "Reference", "group": "financials"},
    {"key": "financials.trans_ref", "language_code": "fr", "value": "Référence", "group": "financials"},
    {"key": "financials.trans_date", "language_code": "en", "value": "Date", "group": "financials"},
    {"key": "financials.trans_date", "language_code": "fr", "value": "Date", "group": "financials"},
    {"key": "financials.trans_desc", "language_code": "en", "value": "Description", "group": "financials"},
    {"key": "financials.trans_desc", "language_code": "fr", "value": "Description", "group": "financials"},
    {"key": "financials.trans_debit", "language_code": "en", "value": "Debit", "group": "financials"},
    {"key": "financials.trans_debit", "language_code": "fr", "value": "Débit", "group": "financials"},
    {"key": "financials.trans_credit", "language_code": "en", "value": "Credit", "group": "financials"},
    {"key": "financials.trans_credit", "language_code": "fr", "value": "Crédit", "group": "financials"},
    {"key": "financials.context_pnl", "language_code": "en", "value": "Profit & Loss", "group": "financials"},
    {"key": "financials.context_pnl", "language_code": "fr", "value": "Pertes et profits", "group": "financials"},
    {"key": "financials.context_balance_sheet", "language_code": "en", "value": "Balance Sheet", "group": "financials"},
    {"key": "financials.context_balance_sheet", "language_code": "fr", "value": "Bilan", "group": "financials"},
    {"key": "financials.context_trial_balance", "language_code": "en", "value": "Trial Balance", "group": "financials"},
    {"key": "financials.context_trial_balance", "language_code": "fr", "value": "Balance de vérification", "group": "financials"},
    {"key": "financials.accounting_points", "language_code": "en", "value": "Accounting Points", "group": "financials"},
    {"key": "financials.accounting_points", "language_code": "fr", "value": "Points comptables", "group": "financials"},
    {"key": "financials.reg_title", "language_code": "en", "value": "Regional Config", "group": "financials"},
    {"key": "financials.reg_title", "language_code": "fr", "value": "Config Régionale", "group": "financials"},
    {"key": "financials.reg_desc", "language_code": "en", "value": "Configure region settings", "group": "financials"},
    {"key": "financials.reg_desc", "language_code": "fr", "value": "Configurer les paramètres régionaux", "group": "financials"},

    # Policy
    {"key": "policy.per_month", "language_code": "en", "value": "/ month", "group": "policy"},
    {"key": "policy.per_month", "language_code": "fr", "value": "/ mois", "group": "policy"},
    {"key": "policy_templates.available_templates", "language_code": "en", "value": "Available Templates", "group": "policy"},
    {"key": "policy_templates.available_templates", "language_code": "fr", "value": "Modèles disponibles", "group": "policy"},
    {"key": "policy_templates.create_template", "language_code": "en", "value": "Create Template", "group": "policy"},
    {"key": "policy_templates.create_template", "language_code": "fr", "value": "Créer un modèle", "group": "policy"},
    {"key": "policy_types.defined_types", "language_code": "en", "value": "Defined Policy Types", "group": "policy"},
    {"key": "policy_types.defined_types", "language_code": "fr", "value": "Types de police définis", "group": "policy"},
    {"key": "policy_types.new_type", "language_code": "en", "value": "New Policy Type", "group": "policy"},
    {"key": "policy_types.new_type", "language_code": "fr", "value": "Nouveau type de police", "group": "policy"},
    {"key": "policy_types.type_name", "language_code": "en", "value": "Type Name", "group": "policy"},
    {"key": "policy_types.type_name", "language_code": "fr", "value": "Nom du type", "group": "policy"},
    {"key": "premium_policies.new_policy", "language_code": "en", "value": "New Policy", "group": "policy"},
    {"key": "premium_policies.new_policy", "language_code": "fr", "value": "Nouvelle police", "group": "policy"},

    # POS
    {"key": "pos.add_pos", "language_code": "en", "value": "Add POS", "group": "pos"},
    {"key": "pos.add_pos", "language_code": "fr", "value": "Ajouter un point de vente", "group": "pos"},
    {"key": "pos.pos_locations", "language_code": "en", "value": "POS Locations", "group": "pos"},
    {"key": "pos.pos_locations", "language_code": "fr", "value": "Emplacements des points de vente", "group": "pos"},

    # Settings Keys
    {"key": "settings.keys.title", "language_code": "en", "value": "API Keys", "group": "settings"},
    {"key": "settings.keys.title", "language_code": "fr", "value": "Clés API", "group": "settings"},
    {"key": "settings.keys.desc", "language_code": "en", "value": "Manage API keys for external access", "group": "settings"},
    {"key": "settings.keys.desc", "language_code": "fr", "value": "Gérer les clés API pour l'accès externe", "group": "settings"},
    {"key": "settings.keys.create_new", "language_code": "en", "value": "Create New Key", "group": "settings"},
    {"key": "settings.keys.create_new", "language_code": "fr", "value": "Créer une nouvelle clé", "group": "settings"},
    {"key": "settings.keys.empty", "language_code": "en", "value": "No API keys found.", "group": "settings"},
    {"key": "settings.keys.empty", "language_code": "fr", "value": "Aucune clé API trouvée.", "group": "settings"},
    {"key": "settings.keys.table.name", "language_code": "en", "value": "Name", "group": "settings"},
    {"key": "settings.keys.table.name", "language_code": "fr", "value": "Nom", "group": "settings"},
    {"key": "settings.keys.table.prefix", "language_code": "en", "value": "Prefix", "group": "settings"},
    {"key": "settings.keys.table.prefix", "language_code": "fr", "value": "Préfixe", "group": "settings"},
    {"key": "settings.keys.table.status", "language_code": "en", "value": "Status", "group": "settings"},
    {"key": "settings.keys.table.status", "language_code": "fr", "value": "Statut", "group": "settings"},
    {"key": "settings.keys.table.created", "language_code": "en", "value": "Created", "group": "settings"},
    {"key": "settings.keys.table.created", "language_code": "fr", "value": "Créé", "group": "settings"},
    {"key": "settings.keys.table.agent_id", "language_code": "en", "value": "Agent ID", "group": "settings"},
    {"key": "settings.keys.table.agent_id", "language_code": "fr", "value": "ID de l'agent", "group": "settings"},
    {"key": "settings.keys.create_title", "language_code": "en", "value": "Create API Key", "group": "settings"},
    {"key": "settings.keys.create_title", "language_code": "fr", "value": "Créer une clé API", "group": "settings"},
    {"key": "settings.keys.create_desc", "language_code": "en", "value": "Generate a new key for integration", "group": "settings"},
    {"key": "settings.keys.create_desc", "language_code": "fr", "value": "Générer une nouvelle clé pour l'intégration", "group": "settings"},
    {"key": "settings.keys.name_label", "language_code": "en", "value": "Key Name", "group": "settings"},
    {"key": "settings.keys.name_label", "language_code": "fr", "value": "Nom de la clé", "group": "settings"},
    {"key": "settings.keys.generate_btn", "language_code": "en", "value": "Generate Key", "group": "settings"},
    {"key": "settings.keys.generate_btn", "language_code": "fr", "value": "Générer la clé", "group": "settings"},
    {"key": "settings.keys.copy_warning", "language_code": "en", "value": "Warning: Copy this key now. You won't be able to see it again!", "group": "settings"},
    {"key": "settings.keys.copy_warning", "language_code": "fr", "value": "Attention : Copiez cette clé maintenant. Vous ne pourrez plus la voir !", "group": "settings"},

    # Settings Regional
    {"key": "settings.regional.title", "language_code": "en", "value": "Regional Settings", "group": "settings"},
    {"key": "settings.regional.title", "language_code": "fr", "value": "Paramètres régionaux", "group": "settings"},
    {"key": "settings.regional.desc", "language_code": "en", "value": "Configure locale and preferences", "group": "settings"},
    {"key": "settings.regional.desc", "language_code": "fr", "value": "Configurer les paramètres régionaux et les préférences", "group": "settings"},
    {"key": "settings.regional.currency", "language_code": "en", "value": "Currency", "group": "settings"},
    {"key": "settings.regional.currency", "language_code": "fr", "value": "Devise", "group": "settings"},
    {"key": "settings.regional.currency_desc", "language_code": "en", "value": "Select your preferred currency", "group": "settings"},
    {"key": "settings.regional.currency_desc", "language_code": "fr", "value": "Sélectionnez votre devise préférée", "group": "settings"},
    {"key": "settings.regional.timezone", "language_code": "en", "value": "Timezone", "group": "settings"},
    {"key": "settings.regional.timezone", "language_code": "fr", "value": "Fuseau horaire", "group": "settings"},
    {"key": "settings.regional.timezone_desc", "language_code": "en", "value": "Set your local timezone", "group": "settings"},
    {"key": "settings.regional.timezone_desc", "language_code": "fr", "value": "Définissez votre fuseau horaire local", "group": "settings"},
    {"key": "settings.regional.date_format", "language_code": "en", "value": "Date Format", "group": "settings"},
    {"key": "settings.regional.date_format", "language_code": "fr", "value": "Format de date", "group": "settings"},
    {"key": "settings.regional.date_format_desc", "language_code": "en", "value": "Choose how dates are displayed", "group": "settings"},
    {"key": "settings.regional.date_format_desc", "language_code": "fr", "value": "Choisissez comment les dates sont affichées", "group": "settings"},

    # Settings Company
    {"key": "settings.header_desc", "language_code": "en", "value": "Manage application settings", "group": "settings"},
    {"key": "settings.header_desc", "language_code": "fr", "value": "Gérer les paramètres de l'application", "group": "settings"},
    {"key": "settings.company.desc", "language_code": "en", "value": "Company Information", "group": "settings"},
    {"key": "settings.company.desc", "language_code": "fr", "value": "Informations sur l'entreprise", "group": "settings"},
    {"key": "settings.company.country", "language_code": "en", "value": "Country", "group": "settings"},
    {"key": "settings.company.country", "language_code": "fr", "value": "Pays", "group": "settings"},
    {"key": "settings.account_name", "language_code": "en", "value": "Account Name", "group": "settings"},
    {"key": "settings.account_name", "language_code": "fr", "value": "Nom du compte", "group": "settings"},
    {"key": "settings.account_number", "language_code": "en", "value": "Account Number", "group": "settings"},
    {"key": "settings.account_number", "language_code": "fr", "value": "Numéro de compte", "group": "settings"},
    {"key": "settings.bank_account_number", "language_code": "en", "value": "Bank Account Number", "group": "settings"},
    {"key": "settings.bank_account_number", "language_code": "fr", "value": "Numéro de compte bancaire", "group": "settings"},
    {"key": "settings.bank_name", "language_code": "en", "value": "Bank Name", "group": "settings"},
    {"key": "settings.bank_name", "language_code": "fr", "value": "Nom de la banque", "group": "settings"},
    {"key": "settings.branch", "language_code": "en", "value": "Branch", "group": "settings"},
    {"key": "settings.branch", "language_code": "fr", "value": "Succursale", "group": "settings"},
    {"key": "settings.mobile_money_account_number", "language_code": "en", "value": "Mobile Money Number", "group": "settings"},
    {"key": "settings.mobile_money_account_number", "language_code": "fr", "value": "Numéro Mobile Money", "group": "settings"},
    {"key": "settings.mobile_money_desc", "language_code": "en", "value": "Mobile Money Configuration", "group": "settings"},
    {"key": "settings.mobile_money_desc", "language_code": "fr", "value": "Configuration Mobile Money", "group": "settings"},
    {"key": "settings.swift_bic_code", "language_code": "en", "value": "SWIFT/BIC Code", "group": "settings"},
    {"key": "settings.swift_bic_code", "language_code": "fr", "value": "Code SWIFT/BIC", "group": "settings"},
    {"key": "settings.uploading", "language_code": "en", "value": "Uploading...", "group": "settings"},
    {"key": "settings.uploading", "language_code": "fr", "value": "Téléchargement...", "group": "settings"},
    
    # Payments
    {"key": "payments.payment_list", "language_code": "en", "value": "Payment List", "group": "payments"},
    {"key": "payments.payment_list", "language_code": "fr", "value": "Liste des paiements", "group": "payments"},
]

def seed_missing_translations():
    print(f"Seeding {len(missing_translations)} missing translations...")
    for t in missing_translations:
        try:
            response = requests.post(API_URL, json=t)
            if response.status_code == 200:
                print(f"Created: {t['key']} ({t['language_code']})")
            elif response.status_code == 400:
                # This might happen if 'check_missing_keys' was wrong or key existed but I missed it.
                # However, re-seeding with updated values is generally safe if the API supports upsert, 
                # but this API returns 400 if exists.
                print(f"Skipped (Exists): {t['key']} ({t['language_code']})")
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    seed_missing_translations()
