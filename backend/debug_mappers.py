
import sys
import os
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, Base, engine
from app.models.company import Company
from app.models.premium_policy import PremiumPolicyType

def check_mappers():
    try:
        from sqlalchemy import inspect
        print("Inspecting Company...")
        insp = inspect(Company)
        print("Company relationships:", insp.relationships.keys())
        
        print("Inspecting PremiumPolicyType...")
        insp_pp = inspect(PremiumPolicyType)
        print("PremiumPolicyType relationships:", insp_pp.relationships.keys())
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mappers()
