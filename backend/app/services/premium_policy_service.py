from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime

from app.models.premium_policy import PremiumPolicyType, PremiumPolicyCriteria
from app.models.client import Client

class PremiumPolicyService:
    def __init__(self, db: Session):
        self.db = db

    def match_eligible_policies(self, company_id: UUID, client_id: UUID) -> Dict[str, Any]:
        """
        Matches a client against all active premium policies based on criteria.
        Returns a dictionary with status and data.
        """
        
        # 1. Check if any active policies exist
        policies = self.db.query(PremiumPolicyType).filter(
            PremiumPolicyType.company_id == company_id,
            PremiumPolicyType.is_active == True
        ).all()
        
        if not policies:
            return {
                "status": "no_policies",
                "message": "There is no premium policy available. You must create a policy first before creating a quote.",
                "data": []
            }

        # 2. Get Client Data
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return {
                "status": "error",
                "message": "Client not found",
                "data": []
            }

        # 3. Identify Required Fields from all active criteria
        # We need to know what fields are generally required to check if client has them.
        required_fields = set()
        all_criteria = self.db.query(PremiumPolicyCriteria).filter(
             PremiumPolicyCriteria.company_id == company_id
        ).all()
        
        for criteria in all_criteria:
            required_fields.add(criteria.field_name)

        # 4. Content Validation
        # Map criteria field names to Client model attributes
        # This mapping needs to be robust. 
        # Standard fields: accident_count, no_claims_years, driving_license_years, employment_status
        
        # Calculate Age
        age = None
        if client.date_of_birth:
             today = date.today()
             age = today.year - client.date_of_birth.year - ((today.month, today.day) < (client.date_of_birth.month, client.date_of_birth.day))

        client_data = {
            "accident_count": client.accident_count,
            "no_claims_years": client.no_claims_years,
            "driving_license_years": client.driving_license_years,
            "employment_status": client.employment_status,
            # Expanded fields
            "age": age,
            "annual_income": client.annual_income,
            "occupation": client.occupation,
            "gender": client.gender,
            "marital_status": client.marital_status,
            "risk_profile": client.risk_profile,
            "residency": client.country,
            "city": client.city,
            "client_type": client.client_type,
            "is_high_risk": client.is_high_risk
        }
        


        # 5. Matching Logic
        eligible_policies = []
        
        for policy in policies:
            is_eligible = True
            
            # Check all criteria associated with this policy
            for criteria in policy.criteria:
                client_value = client_data.get(criteria.field_name)
                
                # Double check if value is missing for this specific policy's specific criteria
                if client_value is None:
                     is_eligible = False
                     break
                
                # Evaluate Rule
                if not self._evaluate_rule(client_value, criteria.operator, criteria.value):
                    is_eligible = False
                    break
            
            if is_eligible:
                eligible_policies.append(policy)

        # 6. determine Recommendation (Simplistic: Lowest Price)
        recommended_id = None
        if eligible_policies:
            # Sort by price ascending
            eligible_policies.sort(key=lambda p: p.price)
            recommended_id = eligible_policies[0].id

        return {
            "status": "success",
            "data": eligible_policies,
            "recommended_id": recommended_id
        }

    def _evaluate_rule(self, actual_value: Any, operator: str, target_value: str) -> bool:
        """Helper to evaluate single rule."""
        try:
            # Convert target to same type as actual if possible, usually int/float
            # Currently assuming numeric comparisons for simpler implementation
            
            # Handle list/in operator
            if operator == 'in':
                options = [x.strip() for x in target_value.split(',')]
                return str(actual_value) in options

            val_num = float(actual_value)
            target_num = float(target_value)
            
            if operator == '>':
                return val_num > target_num
            elif operator == '>=':
                return val_num >= target_num
            elif operator == '<':
                return val_num < target_num
            elif operator == '<=':
                return val_num <= target_num
            elif operator == '=' or operator == '==':
                 return val_num == target_num
                 
            return False
        except Exception:
            # Fallback for string comparison
             if operator == '=' or operator == '==':
                 return str(actual_value).lower() == str(target_value).lower()
             return False
