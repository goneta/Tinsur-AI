import sys
import os
from decimal import Decimal
from sqlalchemy.orm import Session
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.policy_service import PolicyService
from app.models.premium_policy import PremiumPolicyType
from app.models.company import Company

def seed_20_services():
    db = SessionLocal()
    try:
        # Get demo company
        company = db.query(Company).filter(Company.subdomain == "demoinsurance.com").first()
        if not company:
            print("Company not found.")
            return

        print(f"Seeding 20 Premium Services for {company.name}...")

        services_defs = [
            {"en": "Comprehensive cover", "fr": "Couverture tous risques", "price": 0.00, "cat": "Core", "icon": "ShieldCheck"},
            {"en": "Small courtesy car", "fr": "Véhicule de courtoisie (petit modèle)", "price": 2.50, "cat": "Vehicle", "icon": "Car"},
            {"en": "Windscreen cover", "fr": "Garantie bris de glace", "price": 1.50, "cat": "Vehicle", "icon": "GlassWater"},
            {"en": "90-day comprehensive EU cover", "fr": "Couverture tous risques dans l'UE pendant 90 jours", "price": 3.00, "cat": "Travel", "icon": "Globe"},
            {"en": "Uninsured driver promise", "fr": "Promesse conducteur non assuré", "price": 1.20, "cat": "Protection", "icon": "UserCheck"},
            {"en": "Claims portal access", "fr": "Accès au portail de sinistres", "price": 0.00, "cat": "Core", "icon": "Monitor"},
            {"en": "Loss of keys", "fr": "Perte de clés", "price": 0.80, "cat": "Security", "icon": "Key"},
            {"en": "Personal accident cover", "fr": "Assurance accident personnelle", "price": 4.50, "cat": "Protection", "icon": "HeartPulse"},
            {"en": "Personal belongings cover", "fr": "Couverture des effets personnels", "price": 2.00, "cat": "Protection", "icon": "Briefcase"},
            {"en": "Car seats cover", "fr": "Couverture des sièges auto", "price": 1.00, "cat": "Vehicle", "icon": "Baby"},
            {"en": "Theft of keys", "fr": "Vol de clés", "price": 1.50, "cat": "Security", "icon": "Lock"},
            {"en": "New car replacement", "fr": "Remplacement véhicule neuf", "price": 10.00, "cat": "Vehicle", "icon": "Sparkles"},
            {"en": "Misfuelling cover", "fr": "Erreur de carburant", "price": 2.50, "cat": "Vehicle", "icon": "Fuel"},
            {"en": "Onward travel", "fr": "Poursuite du voyage", "price": 3.50, "cat": "Travel", "icon": "Plane"},
            {"en": "Vandalism promise", "fr": "Promesse vandalisme", "price": 1.80, "cat": "Protection", "icon": "AlertTriangle"},
            {"en": "Hotel expenses", "fr": "Frais d'hôtel", "price": 5.00, "cat": "Travel", "icon": "Hotel"},
            {"en": "Legal protection", "fr": "Protection juridique", "price": 6.00, "cat": "Legal", "icon": "Scale"},
            {"en": "Breakdown recovery", "fr": "Dépannage 24/7", "price": 8.50, "cat": "Vehicle", "icon": "Wrench"},
            {"en": "Replacement of locks", "fr": "Remplacement des serrures", "price": 2.00, "cat": "Security", "icon": "KeyRound"},
            {"en": "Wrong fuel recovery", "fr": "Vidange réservoir erreur carburant", "price": 4.00, "cat": "Vehicle", "icon": "Droplets"}
        ]

        # 1. Create/Update Services
        created_services = []
        for s_data in services_defs:
            existing = db.query(PolicyService).filter(
                PolicyService.company_id == company.id,
                PolicyService.name_en == s_data["en"]
            ).first()
            
            if not existing:
                service = PolicyService(
                    company_id=company.id,
                    name_en=s_data["en"],
                    name_fr=s_data["fr"],
                    default_price=Decimal(str(s_data["price"])),
                    category=s_data["cat"],
                    icon_name=s_data["icon"],
                    is_active=True
                )
                db.add(service)
                db.flush()
                created_services.append(service)
            else:
                existing.name_fr = s_data["fr"]
                existing.default_price = Decimal(str(s_data["price"]))
                existing.category = s_data["cat"]
                existing.icon_name = s_data["icon"]
                created_services.append(existing)

        # 2. Update Premium Policy Types with more information
        policies = db.query(PremiumPolicyType).filter(PremiumPolicyType.company_id == company.id).all()
        for p in policies:
            if p.name == "Bronze":
                p.tagline = "Essential protection for experienced drivers"
                p.is_featured = False
                # Limit to 5 services
                p.services = created_services[:5]
            elif p.name == "Silver":
                p.tagline = "Our mid-range cover with EU protection"
                p.is_featured = True
                # Limit to 10 services
                p.services = created_services[:10]
            elif p.name == "Gold":
                p.tagline = "Maximum peace of mind with full comprehensive benefits"
                p.is_featured = False
                # All 20 services
                p.services = created_services

        db.commit()
        print("20 Services Seed Completed.")

    except Exception as e:
        print(f"Error seeding services: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_20_services()
