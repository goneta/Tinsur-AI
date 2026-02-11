from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime

from app.models.premium_policy import PremiumPolicyType, PremiumPolicyCriteria
from app.models.client import Client

class PremiumPolicyService:
    def __init__(self, db: Session):
        self.db = db

    def match_eligible_policies(self, company_id: UUID, client_id: Optional[UUID] = None, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Matches a client against all active premium policies based on criteria.
        Returns a dictionary with status and data.
        
        overrides: Optional dict containing 'vehicle_details' and 'driver_details' from the wizard.
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

        # 2. Get Client Data (if provided)
        client_data = {}
        
        if client_id:
            client = self.db.query(Client).filter(Client.id == client_id).first()
            if not client:
                return {
                    "status": "error",
                    "message": "Client not found",
                    "data": []
                }
            
            # Calculate Age from DB
            age = None
            if client.date_of_birth:
                 today = date.today()
                 age = today.year - client.date_of_birth.year - ((today.month, today.day) < (client.date_of_birth.month, client.date_of_birth.day))

            client_data = {
                "accident_count": client.accident_count,
                "no_claims_years": client.no_claims_years,
                "driving_license_years": client.driving_license_years,
                "employment_status": client.employment_status,
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

        # 3. Identify Required Fields from all active criteria
        # We need to know what fields are generally required to check if client has them.
        required_fields = set()
        all_criteria = self.db.query(PremiumPolicyCriteria).filter(
             PremiumPolicyCriteria.company_id == company_id
        ).all()
        
        for criteria in all_criteria:
            required_fields.add(criteria.field_name)

        # 4. Merge with Overrides and Content Validation
        if overrides:
            driver_details = overrides.get('driver_details') or {}
            vehicle_details = overrides.get('vehicle_details') or {}
            
            # Map Driver details
            if 'age' in driver_details:
                client_data['age'] = driver_details['age']
            if 'date_of_birth' in driver_details and driver_details['date_of_birth']:
                 try:
                     dob = datetime.strptime(driver_details['date_of_birth'], '%Y-%m-%d').date()
                     today = date.today()
                     client_data['age'] = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                 except:
                     pass
                     
            if 'license_years' in driver_details:
                client_data['driving_license_years'] = driver_details['license_years']
            if 'ncd' in driver_details:
                client_data['no_claims_years'] = driver_details['ncd']
                
            # Map Vehicle details
            # Add vehicle keys to client_data for rule evaluation
            if 'value' in vehicle_details:
                client_data['vehicle_value'] = vehicle_details['value']
            if 'vehicle_value' in vehicle_details:
                client_data['vehicle_value'] = vehicle_details['vehicle_value']
            if 'make' in vehicle_details:
                client_data['vehicle_make'] = vehicle_details['make']
            if 'age' in vehicle_details: # Vehicle Age
                client_data['vehicle_age'] = vehicle_details['age']
        


        # 5. Matching Logic
        eligible_policies = []
        missing_fields = set()
        
        for policy in policies:
            is_eligible = True
            
            # Check all criteria associated with this policy
            for criteria in policy.criteria:
                client_value = client_data.get(criteria.field_name)
                
                # Double check if value is missing for this specific policy's specific criteria
                if client_value is None:
                     missing_fields.add(criteria.field_name)
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

        if not eligible_policies and missing_fields:
            return {
                "status": "missing_info",
                "message": "Client information missing for eligibility check.",
                "missing_fields": list(missing_fields),
                "data": []
            }

        return {
            "status": "success",
            "data": eligible_policies,
            "recommended_id": recommended_id
        }

    def _evaluate_rule(self, actual_value: Any, operator: str, target_value: str) -> bool:
        """Helper to evaluate single rule."""
        try:
            # Handle list/in operator (string comparison)
            if operator == 'in':
                options = [x.strip() for x in target_value.split(',')]
                return str(actual_value) in options

            # Handle between operator (numeric)
            if operator == 'between':
                low, high = map(float, target_value.split(','))
                return low <= float(actual_value) <= high

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
