import requests

API_URL = "http://localhost:8000/api/v1/translations/"

translations = [
    # English
    {"key": "auth.login_title", "language_code": "en", "value": "Sign in to your account", "group": "auth"},
    {"key": "auth.email_label", "language_code": "en", "value": "Email", "group": "auth"},
    {"key": "auth.email_placeholder", "language_code": "en", "value": "m@example.com", "group": "auth"},
    {"key": "auth.password_label", "language_code": "en", "value": "Password", "group": "auth"},
    {"key": "auth.password_placeholder", "language_code": "en", "value": "Enter your password", "group": "auth"},
    {"key": "auth.submit_button", "language_code": "en", "value": "Sign In", "group": "auth"},
    {"key": "auth.forgot_password", "language_code": "en", "value": "Forgot your password?", "group": "auth"},
    {"key": "auth.loading", "language_code": "en", "value": "Signing in...", "group": "auth"},
    
    # French
    {"key": "auth.login_title", "language_code": "fr", "value": "Connectez-vous à votre compte", "group": "auth"},
    {"key": "auth.email_label", "language_code": "fr", "value": "Email", "group": "auth"},
    {"key": "auth.email_placeholder", "language_code": "fr", "value": "m@exemple.com", "group": "auth"},
    {"key": "auth.password_label", "language_code": "fr", "value": "Mot de passe", "group": "auth"},
    {"key": "auth.password_placeholder", "language_code": "fr", "value": "Entrez votre mot de passe", "group": "auth"},
    {"key": "auth.submit_button", "language_code": "fr", "value": "Se connecter", "group": "auth"},
    {"key": "auth.forgot_password", "language_code": "fr", "value": "Mot de passe oublié ?", "group": "auth"},
    {"key": "auth.loading", "language_code": "fr", "value": "Connexion en cours...", "group": "auth"},
    
    # Navigation - English
    {"key": "nav.dashboard", "language_code": "en", "value": "Dashboard", "group": "nav"},
    {"key": "nav.clients", "language_code": "en", "value": "Clients", "group": "nav"},
    {"key": "nav.policies", "language_code": "en", "value": "Policies", "group": "nav"},
    {"key": "nav.quotes", "language_code": "en", "value": "Quotes", "group": "nav"},
    {"key": "nav.claims", "language_code": "en", "value": "Claims", "group": "nav"},
    {"key": "nav.finance", "language_code": "en", "value": "Finance", "group": "nav"},
    {"key": "nav.settings", "language_code": "en", "value": "Settings", "group": "nav"},
    {"key": "nav.admin", "language_code": "en", "value": "Admin", "group": "nav"},
    # Groups
    {"key": "nav.overview", "language_code": "en", "value": "Overview", "group": "nav"},
    {"key": "nav.operations", "language_code": "en", "value": "Operations", "group": "nav"},
    {"key": "nav.finance", "language_code": "en", "value": "Finance", "group": "nav"},
    {"key": "nav.management", "language_code": "en", "value": "Management", "group": "nav"},
    {"key": "nav.tools", "language_code": "en", "value": "Tools", "group": "nav"},
    # More items
    {"key": "nav.analytics", "language_code": "en", "value": "Analytics", "group": "nav"},
    {"key": "nav.insurance_clients", "language_code": "en", "value": "Insurance Client", "group": "nav"},
    {"key": "nav.tickets", "language_code": "en", "value": "Support Tickets", "group": "nav"},
    {"key": "nav.accounting", "language_code": "en", "value": "Accounting", "group": "nav"},
    {"key": "nav.regulatory", "language_code": "en", "value": "Executive Financials", "group": "nav"},
    {"key": "nav.commissions", "language_code": "en", "value": "Commissions", "group": "nav"},
    {"key": "nav.financial_reports", "language_code": "en", "value": "Financial Reports", "group": "nav"},
    {"key": "nav.decisions", "language_code": "en", "value": "Decision Hub", "group": "nav"},
    {"key": "nav.employees", "language_code": "en", "value": "Employees", "group": "nav"},
    {"key": "nav.payroll", "language_code": "en", "value": "Payroll", "group": "nav"},
    {"key": "nav.templates", "language_code": "en", "value": "Policy Templates", "group": "nav"},
    {"key": "nav.policy_types", "language_code": "en", "value": "Policy Types", "group": "nav"},
    {"key": "nav.pos", "language_code": "en", "value": "POS Management", "group": "nav"},
    {"key": "nav.premium_policies", "language_code": "en", "value": "Premium Policies", "group": "nav"},
    {"key": "nav.services", "language_code": "en", "value": "Policy Services", "group": "nav"},
    {"key": "nav.ai_manager", "language_code": "en", "value": "AI Agent Manager", "group": "nav"},
    {"key": "nav.collaboration", "language_code": "en", "value": "Collaboration", "group": "nav"},
    {"key": "nav.loyalty", "language_code": "en", "value": "Loyalty Program", "group": "nav"},
    {"key": "nav.telematics", "language_code": "en", "value": "Telematics", "group": "nav"},


    # Navigation - French
    {"key": "nav.dashboard", "language_code": "fr", "value": "Tableau de bord", "group": "nav"},
    {"key": "nav.clients", "language_code": "fr", "value": "Clients", "group": "nav"},
    {"key": "nav.policies", "language_code": "fr", "value": "Polices", "group": "nav"},
    {"key": "nav.quotes", "language_code": "fr", "value": "Devis", "group": "nav"},
    {"key": "nav.claims", "language_code": "fr", "value": "Sinistres", "group": "nav"},
    {"key": "nav.finance", "language_code": "fr", "value": "Finance", "group": "nav"},
    {"key": "nav.settings", "language_code": "fr", "value": "Paramètres", "group": "nav"},
    {"key": "nav.admin", "language_code": "fr", "value": "Administration", "group": "nav"},
     # Groups FR
    {"key": "nav.overview", "language_code": "fr", "value": "Vue d'ensemble", "group": "nav"},
    {"key": "nav.operations", "language_code": "fr", "value": "Opérations", "group": "nav"},
    {"key": "nav.management", "language_code": "fr", "value": "Gestion", "group": "nav"},
    {"key": "nav.tools", "language_code": "fr", "value": "Outils", "group": "nav"},
    # More items FR
    {"key": "nav.analytics", "language_code": "fr", "value": "Analytique", "group": "nav"},
    {"key": "nav.insurance_clients", "language_code": "fr", "value": "Clients Assurance", "group": "nav"},
    {"key": "nav.tickets", "language_code": "fr", "value": "Tickets Support", "group": "nav"},
    {"key": "nav.accounting", "language_code": "fr", "value": "Comptabilité", "group": "nav"},
    {"key": "nav.regulatory", "language_code": "fr", "value": "Rapports Financiers", "group": "nav"},
    {"key": "nav.commissions", "language_code": "fr", "value": "Commissions", "group": "nav"},
    {"key": "nav.financial_reports", "language_code": "fr", "value": "Rapports Financiers", "group": "nav"},
    {"key": "nav.decisions", "language_code": "fr", "value": "Centre de Décision", "group": "nav"},
    {"key": "nav.employees", "language_code": "fr", "value": "Employés", "group": "nav"},
    {"key": "nav.payroll", "language_code": "fr", "value": "Paie", "group": "nav"},
    {"key": "nav.templates", "language_code": "fr", "value": "Modèles de Police", "group": "nav"},
    {"key": "nav.policy_types", "language_code": "fr", "value": "Types de Police", "group": "nav"},
    {"key": "nav.pos", "language_code": "fr", "value": "Gestion POS", "group": "nav"},
    {"key": "nav.premium_policies", "language_code": "fr", "value": "Polices Premium", "group": "nav"},
    {"key": "nav.services", "language_code": "fr", "value": "Services de Police", "group": "nav"},
    {"key": "nav.ai_manager", "language_code": "fr", "value": "Gestion Agents IA", "group": "nav"},
    {"key": "nav.collaboration", "language_code": "fr", "value": "Collaboration", "group": "nav"},
    {"key": "nav.loyalty", "language_code": "fr", "value": "Programme Fidélité", "group": "nav"},
    {"key": "nav.telematics", "language_code": "fr", "value": "Télématique", "group": "nav"},

    # Common - English
    {"key": "common.premium", "language_code": "en", "value": "Premium", "group": "common"},
    {"key": "common.deductible", "language_code": "en", "value": "Deductible", "group": "common"},
    {"key": "common.coverage", "language_code": "en", "value": "Coverage", "group": "common"},
    {"key": "common.amount", "language_code": "en", "value": "Amount", "group": "common"},
    {"key": "common.status", "language_code": "en", "value": "Status", "group": "common"},
    {"key": "common.actions", "language_code": "en", "value": "Actions", "group": "common"},
    {"key": "common.cancel", "language_code": "en", "value": "Cancel", "group": "common"},
    {"key": "common.save", "language_code": "en", "value": "Save", "group": "common"},
    {"key": "common.edit", "language_code": "en", "value": "Edit", "group": "common"},
    {"key": "common.delete", "language_code": "en", "value": "Delete", "group": "common"},
    {"key": "common.submit", "language_code": "en", "value": "Submit", "group": "common"},

    # Common - French
    {"key": "common.premium", "language_code": "fr", "value": "Prime", "group": "common"},
    {"key": "common.deductible", "language_code": "fr", "value": "Franchise", "group": "common"},
    {"key": "common.coverage", "language_code": "fr", "value": "Couverture", "group": "common"},
    {"key": "common.amount", "language_code": "fr", "value": "Montant", "group": "common"},
    {"key": "common.status", "language_code": "fr", "value": "Statut", "group": "common"},
    {"key": "common.actions", "language_code": "fr", "value": "Actions", "group": "common"},
    {"key": "common.cancel", "language_code": "fr", "value": "Annuler", "group": "common"},
    {"key": "common.save", "language_code": "fr", "value": "Enregistrer", "group": "common"},
    {"key": "common.edit", "language_code": "fr", "value": "Modifier", "group": "common"},
    {"key": "common.delete", "language_code": "fr", "value": "Supprimer", "group": "common"},
    {"key": "common.submit", "language_code": "fr", "value": "Soumettre", "group": "common"},

    # Dashboard - English
    {"key": "dashboard.welcome", "language_code": "en", "value": "Welcome back", "group": "dashboard"},
    {"key": "dashboard.overview", "language_code": "en", "value": "Overview", "group": "dashboard"},
    {"key": "dashboard.subtitle", "language_code": "en", "value": "Here's what's happening with your insurance portfolio today.", "group": "dashboard"},
    {"key": "dashboard.download_report", "language_code": "en", "value": "Download Report", "group": "dashboard"},
    {"key": "dashboard.total_clients", "language_code": "en", "value": "Total Clients", "group": "dashboard"},
    {"key": "dashboard.active_policies", "language_code": "en", "value": "Active Policies", "group": "dashboard"},
    {"key": "dashboard.pending_quotes", "language_code": "en", "value": "Pending Quotes", "group": "dashboard"},
    {"key": "dashboard.monthly_revenue", "language_code": "en", "value": "Monthly Revenue", "group": "dashboard"},
    {"key": "dashboard.recent_activity", "language_code": "en", "value": "Recent Activity", "group": "dashboard"},
    {"key": "dashboard.recent_activity_desc", "language_code": "en", "value": "Recent actions across all your policies and clients.", "group": "dashboard"},
    {"key": "dashboard.no_activity", "language_code": "en", "value": "No recent activity found.", "group": "dashboard"},
    {"key": "dashboard.quick_actions", "language_code": "en", "value": "Quick Actions", "group": "dashboard"},
    {"key": "dashboard.quick_actions_desc", "language_code": "en", "value": "Common tasks and operations.", "group": "dashboard"},
    {"key": "dashboard.create_quote", "language_code": "en", "value": "Create New Quote", "group": "dashboard"},
    {"key": "dashboard.add_client", "language_code": "en", "value": "Add New Client", "group": "dashboard"},
    {"key": "dashboard.process_payment", "language_code": "en", "value": "Process Payment", "group": "dashboard"},
    {"key": "dashboard.from_last_month", "language_code": "en", "value": "from last month", "group": "dashboard"},

    # Dashboard - French
    {"key": "dashboard.welcome", "language_code": "fr", "value": "Bon retour", "group": "dashboard"},
    {"key": "dashboard.overview", "language_code": "fr", "value": "Vue d'ensemble", "group": "dashboard"},
    {"key": "dashboard.subtitle", "language_code": "fr", "value": "Voici ce qui se passe avec votre portefeuille d'assurance aujourd'hui.", "group": "dashboard"},
    {"key": "dashboard.download_report", "language_code": "fr", "value": "Télécharger le rapport", "group": "dashboard"},
    {"key": "dashboard.total_clients", "language_code": "fr", "value": "Total Clients", "group": "dashboard"},
    {"key": "dashboard.active_policies", "language_code": "fr", "value": "Polices Actives", "group": "dashboard"},
    {"key": "dashboard.pending_quotes", "language_code": "fr", "value": "Devis en Attente", "group": "dashboard"},
    {"key": "dashboard.monthly_revenue", "language_code": "fr", "value": "Revenu Mensuel", "group": "dashboard"},
    {"key": "dashboard.recent_activity", "language_code": "fr", "value": "Activité Récente", "group": "dashboard"},
    {"key": "dashboard.recent_activity_desc", "language_code": "fr", "value": "Actions récentes sur toutes vos polices et clients.", "group": "dashboard"},
    {"key": "dashboard.no_activity", "language_code": "fr", "value": "Aucune activité récente trouvée.", "group": "dashboard"},
    {"key": "dashboard.quick_actions", "language_code": "fr", "value": "Actions Rapides", "group": "dashboard"},
    {"key": "dashboard.quick_actions_desc", "language_code": "fr", "value": "Tâches et opérations courantes.", "group": "dashboard"},
    {"key": "dashboard.create_quote", "language_code": "fr", "value": "Créer un Nouveau Devis", "group": "dashboard"},
    {"key": "dashboard.add_client", "language_code": "fr", "value": "Ajouter un Nouveau Client", "group": "dashboard"},
    {"key": "dashboard.process_payment", "language_code": "fr", "value": "Traiter un Paiement", "group": "dashboard"},
    {"key": "dashboard.from_last_month", "language_code": "fr", "value": "depuis le mois dernier", "group": "dashboard"},

    # Clients - English
    {"key": "clients.title", "language_code": "en", "value": "Clients", "group": "clients"},
    {"key": "clients.subtitle", "language_code": "en", "value": "Manage your insurance clients", "group": "clients"},
    {"key": "clients.new_client", "language_code": "en", "value": "New Client", "group": "clients"},
    {"key": "clients.phone", "language_code": "en", "value": "Phone", "group": "clients"},
    {"key": "clients.type", "language_code": "en", "value": "Type", "group": "clients"},

    # Clients - French
    {"key": "clients.title", "language_code": "fr", "value": "Clients", "group": "clients"},
    {"key": "clients.subtitle", "language_code": "fr", "value": "Gérez vos clients d'assurance", "group": "clients"},
    # Policies - English
    {"key": "policies.title", "language_code": "en", "value": "Policies", "group": "policies"},
    {"key": "policies.subtitle", "language_code": "en", "value": "Manage insurance policies and renewals.", "group": "policies"},
    {"key": "policies.new_policy", "language_code": "en", "value": "New Policy", "group": "policies"},
    {"key": "policies.all_policies", "language_code": "en", "value": "All Policies", "group": "policies"},
    {"key": "policies.list_desc", "language_code": "en", "value": "A list of all policies in the system including their status and premiums.", "group": "policies"},
    {"key": "policies.no_policies", "language_code": "en", "value": "No policies found", "group": "policies"},
    {"key": "policies.no_policies_desc", "language_code": "en", "value": "You haven't created any insurance policies yet. Start by creating a new policy or converting a quote.", "group": "policies"},
    {"key": "policies.create_first", "language_code": "en", "value": "Create First Policy", "group": "policies"},

    # Policies - French
    {"key": "policies.title", "language_code": "fr", "value": "Polices", "group": "policies"},
    {"key": "policies.subtitle", "language_code": "fr", "value": "Gérez les polices d'assurance et les renouvellements.", "group": "policies"},
    {"key": "policies.new_policy", "language_code": "fr", "value": "Nouvelle Police", "group": "policies"},
    {"key": "policies.all_policies", "language_code": "fr", "value": "Toutes les Polices", "group": "policies"},
    {"key": "policies.list_desc", "language_code": "fr", "value": "Une liste de toutes les polices du système incluant leur statut et primes.", "group": "policies"},
    {"key": "policies.no_policies", "language_code": "fr", "value": "Aucune police trouvée", "group": "policies"},
    {"key": "policies.no_policies_desc", "language_code": "fr", "value": "Vous n'avez pas encore créé de police d'assurance. Commencez par créer une nouvelle police ou convertir un devis.", "group": "policies"},
    {"key": "policies.create_first", "language_code": "fr", "value": "Créer la Première Police", "group": "policies"},
    
    # Claims - English
    {"key": "claims.title", "language_code": "en", "value": "Claims Management", "group": "claims"},
    {"key": "claims.subtitle", "language_code": "en", "value": "View and process insurance claims.", "group": "claims"},
    {"key": "claims.new_claim", "language_code": "en", "value": "New Claim", "group": "claims"},
    {"key": "claims.no_claims", "language_code": "en", "value": "No claims to process", "group": "claims"},
    {"key": "claims.no_claims_desc", "language_code": "en", "value": "There are currently no insurance claims in the system. When clients submit claims, they will appear here for review.", "group": "claims"},
    {"key": "claims.create_first", "language_code": "en", "value": "Create First Claim", "group": "claims"},

    # Claims - French
    {"key": "claims.title", "language_code": "fr", "value": "Gestion des Sinistres", "group": "claims"},
    {"key": "claims.subtitle", "language_code": "fr", "value": "Voir et traiter les réclamations d'assurance.", "group": "claims"},
    {"key": "claims.new_claim", "language_code": "fr", "value": "Nouveau Sinistre", "group": "claims"},
    {"key": "claims.no_claims", "language_code": "fr", "value": "Aucun sinistre à traiter", "group": "claims"},
    {"key": "claims.no_claims_desc", "language_code": "fr", "value": "Il n'y a actuellement aucun sinistre dans le système. Lorsque les clients soumettent des réclamations, elles apparaîtront ici pour examen.", "group": "claims"},
    {"key": "claims.create_first", "language_code": "fr", "value": "Créer le Premier Sinistre", "group": "claims"},

    # AI Agent - English
    {"key": "aiAgent.title", "language_code": "en", "value": "AI Agent Manager", "group": "aiAgent"},
    {"key": "aiAgent.orchestrator_active", "language_code": "en", "value": "Orchestrator Active", "group": "aiAgent"},
    {"key": "aiAgent.welcome", "language_code": "en", "value": "Welcome to the **AI Agent Manager**.\n\nI am connected to the **Agent Mesh**. You can ask me to perform operations like:\n\n* \"Create a new quote for Client X\"\n* \"Analyze claims performance from last month\"\n* \"Add a new user to the system\"\n\nUse the **+** menu to upload files or access advanced tools.", "group": "aiAgent"},
    {"key": "aiAgent.modify_elements", "language_code": "en", "value": "Modify Elements", "group": "aiAgent"},
    {"key": "aiAgent.edit", "language_code": "en", "value": "Edit", "group": "aiAgent"},
    {"key": "aiAgent.keep", "language_code": "en", "value": "Keep", "group": "aiAgent"},
    {"key": "aiAgent.sync_active", "language_code": "en", "value": "Form synchronization active", "group": "aiAgent"},
    {"key": "aiAgent.thinking", "language_code": "en", "value": "AI is thinking...", "group": "aiAgent"},
    {"key": "aiAgent.placeholder", "language_code": "en", "value": "Ask anything...", "group": "aiAgent"},
    {"key": "aiAgent.disclaimer", "language_code": "en", "value": "The AI Agent Manager can make mistakes. Please verify critical actions.", "group": "aiAgent"},
    {"key": "aiAgent.validated", "language_code": "en", "value": "Validated and Saved", "group": "aiAgent"},
    {"key": "aiAgent.validation_failed", "language_code": "en", "value": "Validation Failed", "group": "aiAgent"},
    {"key": "aiAgent.progress_updated", "language_code": "en", "value": "Progress Updated", "group": "aiAgent"},
    {"key": "aiAgent.preview_updated", "language_code": "en", "value": "Preview Updated", "group": "aiAgent"},
    {"key": "aiAgent.action_required", "language_code": "en", "value": "Action Required", "group": "aiAgent"},

    # AI Agent - French
    {"key": "aiAgent.title", "language_code": "fr", "value": "Gestionnaire d'Agent IA", "group": "aiAgent"},
    {"key": "aiAgent.orchestrator_active", "language_code": "fr", "value": "Orchestrateur Actif", "group": "aiAgent"},
    {"key": "aiAgent.welcome", "language_code": "fr", "value": "Bienvenue dans le **Gestionnaire d'Agent IA**.\n\nJe suis connecté au **Maillage d'Agents**. Vous pouvez me demander d'effectuer des opérations comme :\n\n* \"Créer un nouveau devis pour Client X\"\n* \"Analyser la performance des sinistres du mois dernier\"\n* \"Ajouter un nouvel utilisateur au système\"\n\nUtilisez le menu **+** pour télécharger des fichiers ou accéder à des outils avancés.", "group": "aiAgent"},
    {"key": "aiAgent.modify_elements", "language_code": "fr", "value": "Modifier les Éléments", "group": "aiAgent"},
    {"key": "aiAgent.edit", "language_code": "fr", "value": "Modifier", "group": "aiAgent"},
    {"key": "aiAgent.keep", "language_code": "fr", "value": "Garder", "group": "aiAgent"},
    {"key": "aiAgent.sync_active", "language_code": "fr", "value": "Synchronisation du formulaire active", "group": "aiAgent"},
    {"key": "aiAgent.thinking", "language_code": "fr", "value": "L'IA réfléchit...", "group": "aiAgent"},
    {"key": "aiAgent.placeholder", "language_code": "fr", "value": "Demandez n'importe quoi...", "group": "aiAgent"},
    {"key": "aiAgent.disclaimer", "language_code": "fr", "value": "Le Gestionnaire d'Agent IA peut faire des erreurs. Veuillez vérifier les actions critiques.", "group": "aiAgent"},
    {"key": "aiAgent.validated", "language_code": "fr", "value": "Validé et Enregistré", "group": "aiAgent"},
    {"key": "aiAgent.validation_failed", "language_code": "fr", "value": "Échec de la Validation", "group": "aiAgent"},
    {"key": "aiAgent.progress_updated", "language_code": "fr", "value": "Progression Mise à Jour", "group": "aiAgent"},
    {"key": "aiAgent.preview_updated", "language_code": "fr", "value": "Aperçu Mis à Jour", "group": "aiAgent"},
    {"key": "aiAgent.action_required", "language_code": "fr", "value": "Action Requise", "group": "aiAgent"},
]

def seed_translations():
    print("Seeding translations...")
    for t in translations:
        try:
            response = requests.post(API_URL, json=t)
            if response.status_code == 200:
                print(f"Created: {t['key']} ({t['language_code']})")
            elif response.status_code == 400:
                print(f"Skipped (Exists): {t['key']} ({t['language_code']})")
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    seed_translations()
