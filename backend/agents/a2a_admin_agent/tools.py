import os
import sys
import uuid
import json
import logging
from google.adk.tools import tool
from typing import Optional
from decimal import Decimal

logger = logging.getLogger(__name__)

def _get_backend_root():
    """Get the backend root directory and add to sys.path if needed."""
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if root not in sys.path:
        sys.path.append(root)
    return root

@tool
def create_premium_policy_type(company_id: str, name: str, description: str, price: float, excess: float = 0.0, criteria_ids_json: str = "[]", service_ids_json: str = "[]") -> str:
    """
    Creates a new premium policy type for an insurance company.
    criteria_ids_json: JSON array of criteria UUID strings to attach.
    service_ids_json: JSON array of service UUID strings to attach.
    Returns the created policy type details.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.premium_policy import PremiumPolicyType, PremiumPolicyCriteria
        from app.models.policy_service import PolicyService

        criteria_ids = json.loads(criteria_ids_json) if criteria_ids_json else []
        service_ids = json.loads(service_ids_json) if service_ids_json else []

        db = SessionLocal()
        try:
            policy_type = PremiumPolicyType(
                id=uuid.uuid4(),
                company_id=uuid.UUID(company_id),
                name=name,
                description=description,
                price=Decimal(str(price)),
                excess=Decimal(str(excess)),
                is_active=True
            )

            # Attach criteria
            if criteria_ids:
                criteria = db.query(PremiumPolicyCriteria).filter(
                    PremiumPolicyCriteria.id.in_([uuid.UUID(c) for c in criteria_ids]),
                    PremiumPolicyCriteria.company_id == uuid.UUID(company_id)
                ).all()
                policy_type.criteria = criteria

            # Attach services
            if service_ids:
                services = db.query(PolicyService).filter(
                    PolicyService.id.in_([uuid.UUID(s) for s in service_ids]),
                    PolicyService.company_id == uuid.UUID(company_id)
                ).all()
                policy_type.services = services

            db.add(policy_type)
            db.commit()
            db.refresh(policy_type)

            return json.dumps({
                "status": "success",
                "message": f"Premium policy '{name}' created successfully.",
                "policy_type": {
                    "id": str(policy_type.id),
                    "name": policy_type.name,
                    "description": policy_type.description,
                    "price": float(policy_type.price),
                    "excess": float(policy_type.excess),
                    "criteria_count": len(criteria_ids),
                    "services_count": len(service_ids)
                }
            })
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error creating premium policy type: {e}")
        return json.dumps({"status": "error", "message": str(e)})


@tool
def list_premium_policy_types(company_id: str) -> str:
    """
    Lists all premium policy types for a company.
    Returns a JSON array of policy types with their criteria and services.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.premium_policy import PremiumPolicyType
        from sqlalchemy.orm import joinedload

        db = SessionLocal()
        try:
            policies = db.query(PremiumPolicyType).options(
                joinedload(PremiumPolicyType.criteria),
                joinedload(PremiumPolicyType.services)
            ).filter(
                PremiumPolicyType.company_id == uuid.UUID(company_id)
            ).all()

            result = [{
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "price": float(p.price),
                "excess": float(p.excess),
                "is_active": p.is_active,
                "criteria": [{"id": str(c.id), "name": c.name, "field_name": c.field_name, "operator": c.operator, "value": c.value} for c in p.criteria],
                "services": [{"id": str(s.id), "name_en": s.name_en, "name_fr": getattr(s, 'name_fr', '')} for s in p.services]
            } for p in policies]

            return json.dumps({"status": "success", "policies": result, "count": len(result)})
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error listing premium policy types: {e}")
        return json.dumps({"status": "error", "message": str(e)})


@tool
def update_premium_policy_type(policy_type_id: str, company_id: str, name: str = None, description: str = None, price: float = None, excess: float = None, is_active: bool = None) -> str:
    """
    Updates an existing premium policy type. Only provided fields are updated.
    Returns the updated policy type details.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.premium_policy import PremiumPolicyType

        db = SessionLocal()
        try:
            policy = db.query(PremiumPolicyType).filter(
                PremiumPolicyType.id == uuid.UUID(policy_type_id),
                PremiumPolicyType.company_id == uuid.UUID(company_id)
            ).first()

            if not policy:
                return json.dumps({"status": "error", "message": "Premium policy type not found"})

            if name is not None:
                policy.name = name
            if description is not None:
                policy.description = description
            if price is not None:
                policy.price = Decimal(str(price))
            if excess is not None:
                policy.excess = Decimal(str(excess))
            if is_active is not None:
                policy.is_active = is_active

            db.commit()
            return json.dumps({"status": "success", "message": f"Policy type '{policy.name}' updated successfully."})
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error updating premium policy type: {e}")
        return json.dumps({"status": "error", "message": str(e)})


@tool
def delete_premium_policy_type(policy_type_id: str, company_id: str) -> str:
    """
    Deletes a premium policy type (soft or hard delete depending on implementation).
    Returns confirmation of deletion.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.premium_policy import PremiumPolicyType

        db = SessionLocal()
        try:
            policy = db.query(PremiumPolicyType).filter(
                PremiumPolicyType.id == uuid.UUID(policy_type_id),
                PremiumPolicyType.company_id == uuid.UUID(company_id)
            ).first()

            if not policy:
                return json.dumps({"status": "error", "message": "Premium policy type not found"})

            policy_name = policy.name
            db.delete(policy)
            db.commit()

            return json.dumps({
                "status": "success",
                "message": f"Premium policy type '{policy_name}' has been deleted successfully."
            })
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error deleting premium policy type: {e}")
        return json.dumps({"status": "error", "message": str(e)})


@tool
def create_eligibility_criteria(company_id: str, name: str, description: str, field_name: str, operator: str, value: str) -> str:
    """
    Creates a new eligibility criteria rule for premium policy matching.
    field_name: The client field to check (e.g., 'age', 'driving_license_years', 'accident_count', 'no_claims_years', 'vehicle_value', 'employment_status')
    operator: Comparison operator ('>', '>=', '<', '<=', '=', 'between', 'in')
    value: The target value (e.g., '25' for age > 25, '18,65' for age between 18 and 65)
    Returns the created criteria details.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.premium_policy import PremiumPolicyCriteria

        valid_operators = ['>', '>=', '<', '<=', '=', '==', 'between', 'in']
        if operator not in valid_operators:
            return json.dumps({"status": "error", "message": f"Invalid operator. Must be one of: {valid_operators}"})

        db = SessionLocal()
        try:
            criteria = PremiumPolicyCriteria(
                id=uuid.uuid4(),
                company_id=uuid.UUID(company_id),
                name=name,
                description=description,
                field_name=field_name,
                operator=operator,
                value=value
            )
            db.add(criteria)
            db.commit()
            db.refresh(criteria)

            return json.dumps({
                "status": "success",
                "message": f"Criteria '{name}' created successfully.",
                "criteria": {
                    "id": str(criteria.id),
                    "name": criteria.name,
                    "field_name": criteria.field_name,
                    "operator": criteria.operator,
                    "value": criteria.value
                }
            })
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error creating eligibility criteria: {e}")
        return json.dumps({"status": "error", "message": str(e)})


@tool
def list_eligibility_criteria(company_id: str) -> str:
    """
    Lists all eligibility criteria for a company.
    Returns a JSON array of criteria rules.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.premium_policy import PremiumPolicyCriteria

        db = SessionLocal()
        try:
            criteria = db.query(PremiumPolicyCriteria).filter(
                PremiumPolicyCriteria.company_id == uuid.UUID(company_id)
            ).all()

            result = [{
                "id": str(c.id),
                "name": c.name,
                "description": c.description,
                "field_name": c.field_name,
                "operator": c.operator,
                "value": c.value
            } for c in criteria]

            return json.dumps({"status": "success", "criteria": result, "count": len(result)})
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error listing eligibility criteria: {e}")
        return json.dumps({"status": "error", "message": str(e)})


@tool
def update_eligibility_criteria(criteria_id: str, company_id: str, name: str = None, description: str = None, field_name: str = None, operator: str = None, value: str = None) -> str:
    """
    Updates an existing eligibility criteria. Only provided fields are updated.
    Returns the updated criteria details.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.premium_policy import PremiumPolicyCriteria

        valid_operators = ['>', '>=', '<', '<=', '=', '==', 'between', 'in']
        if operator is not None and operator not in valid_operators:
            return json.dumps({"status": "error", "message": f"Invalid operator. Must be one of: {valid_operators}"})

        db = SessionLocal()
        try:
            criteria = db.query(PremiumPolicyCriteria).filter(
                PremiumPolicyCriteria.id == uuid.UUID(criteria_id),
                PremiumPolicyCriteria.company_id == uuid.UUID(company_id)
            ).first()

            if not criteria:
                return json.dumps({"status": "error", "message": "Eligibility criteria not found"})

            if name is not None:
                criteria.name = name
            if description is not None:
                criteria.description = description
            if field_name is not None:
                criteria.field_name = field_name
            if operator is not None:
                criteria.operator = operator
            if value is not None:
                criteria.value = value

            db.commit()
            return json.dumps({"status": "success", "message": f"Criteria '{criteria.name}' updated successfully."})
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error updating eligibility criteria: {e}")
        return json.dumps({"status": "error", "message": str(e)})


@tool
def delete_eligibility_criteria(criteria_id: str, company_id: str) -> str:
    """
    Deletes an eligibility criteria rule.
    Returns confirmation of deletion.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.premium_policy import PremiumPolicyCriteria

        db = SessionLocal()
        try:
            criteria = db.query(PremiumPolicyCriteria).filter(
                PremiumPolicyCriteria.id == uuid.UUID(criteria_id),
                PremiumPolicyCriteria.company_id == uuid.UUID(company_id)
            ).first()

            if not criteria:
                return json.dumps({"status": "error", "message": "Eligibility criteria not found"})

            criteria_name = criteria.name
            db.delete(criteria)
            db.commit()

            return json.dumps({
                "status": "success",
                "message": f"Criteria '{criteria_name}' has been deleted successfully."
            })
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error deleting eligibility criteria: {e}")
        return json.dumps({"status": "error", "message": str(e)})


@tool
def create_policy_service(company_id: str, name_en: str, name_fr: str = None, description_en: str = "", description_fr: str = "", default_price: float = 0.0, category: str = "Other") -> str:
    """
    Creates a new policy service (add-on or coverage option).
    Services can be attached to premium policy types.
    Returns the created service details.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.policy_service import PolicyService

        db = SessionLocal()
        try:
            service = PolicyService(
                id=uuid.uuid4(),
                company_id=uuid.UUID(company_id),
                name_en=name_en,
                name_fr=name_fr or name_en,
                description=description_en,  # Using description field from model
                default_price=Decimal(str(default_price)),
                category=category,
                is_active=True
            )
            db.add(service)
            db.commit()
            db.refresh(service)

            return json.dumps({
                "status": "success",
                "message": f"Policy service '{name_en}' created successfully.",
                "service": {
                    "id": str(service.id),
                    "name_en": service.name_en,
                    "name_fr": service.name_fr,
                    "category": service.category,
                    "default_price": float(service.default_price)
                }
            })
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error creating policy service: {e}")
        return json.dumps({"status": "error", "message": str(e)})


@tool
def list_policy_services(company_id: str) -> str:
    """
    Lists all policy services for a company.
    Returns a JSON array of services.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.policy_service import PolicyService

        db = SessionLocal()
        try:
            services = db.query(PolicyService).filter(
                PolicyService.company_id == uuid.UUID(company_id)
            ).all()

            result = [{
                "id": str(s.id),
                "name_en": s.name_en,
                "name_fr": getattr(s, 'name_fr', ''),
                "description": getattr(s, 'description', ''),
                "category": getattr(s, 'category', 'Other'),
                "default_price": float(s.default_price),
                "is_active": s.is_active
            } for s in services]

            return json.dumps({"status": "success", "services": result, "count": len(result)})
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error listing policy services: {e}")
        return json.dumps({"status": "error", "message": str(e)})


@tool
def update_policy_service(service_id: str, company_id: str, name_en: str = None, name_fr: str = None, description_en: str = None, default_price: float = None, is_active: bool = None, category: str = None) -> str:
    """
    Updates an existing policy service. Only provided fields are updated.
    Returns the updated service details.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.policy_service import PolicyService

        db = SessionLocal()
        try:
            service = db.query(PolicyService).filter(
                PolicyService.id == uuid.UUID(service_id),
                PolicyService.company_id == uuid.UUID(company_id)
            ).first()

            if not service:
                return json.dumps({"status": "error", "message": "Policy service not found"})

            if name_en is not None:
                service.name_en = name_en
            if name_fr is not None:
                service.name_fr = name_fr
            if description_en is not None:
                service.description = description_en
            if default_price is not None:
                service.default_price = Decimal(str(default_price))
            if is_active is not None:
                service.is_active = is_active
            if category is not None:
                service.category = category

            db.commit()
            return json.dumps({"status": "success", "message": f"Policy service '{service.name_en}' updated successfully."})
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error updating policy service: {e}")
        return json.dumps({"status": "error", "message": str(e)})


@tool
def delete_policy_service(service_id: str, company_id: str) -> str:
    """
    Deletes a policy service.
    Returns confirmation of deletion.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.policy_service import PolicyService

        db = SessionLocal()
        try:
            service = db.query(PolicyService).filter(
                PolicyService.id == uuid.UUID(service_id),
                PolicyService.company_id == uuid.UUID(company_id)
            ).first()

            if not service:
                return json.dumps({"status": "error", "message": "Policy service not found"})

            service_name = service.name_en
            db.delete(service)
            db.commit()

            return json.dumps({
                "status": "success",
                "message": f"Policy service '{service_name}' has been deleted successfully."
            })
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error deleting policy service: {e}")
        return json.dumps({"status": "error", "message": str(e)})


@tool
def get_company_dashboard_stats(company_id: str) -> str:
    """
    Gets key statistics and KPIs for a company dashboard.
    Returns counts of policies, claims, quotes, clients, and financial summaries.
    Useful for generating analysis reports.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.policy import Policy
        from app.models.quote import Quote
        from app.models.claim import Claim
        from app.models.client import Client
        from sqlalchemy import func

        db = SessionLocal()
        try:
            cid = uuid.UUID(company_id)

            active_policies = db.query(func.count(Policy.id)).filter(Policy.company_id == cid, Policy.status == 'active').scalar() or 0
            total_quotes = db.query(func.count(Quote.id)).filter(Quote.company_id == cid).scalar() or 0
            pending_claims = db.query(func.count(Claim.id)).filter(Claim.company_id == cid, Claim.status == 'pending').scalar() or 0
            total_clients = db.query(func.count(Client.id)).filter(Client.company_id == cid).scalar() or 0

            total_premium = db.query(func.sum(Policy.premium_amount)).filter(Policy.company_id == cid, Policy.status == 'active').scalar() or 0
            total_coverage = db.query(func.sum(Policy.coverage_amount)).filter(Policy.company_id == cid, Policy.status == 'active').scalar() or 0

            return json.dumps({
                "status": "success",
                "stats": {
                    "active_policies": active_policies,
                    "total_quotes": total_quotes,
                    "pending_claims": pending_claims,
                    "total_clients": total_clients,
                    "total_premium_revenue": float(total_premium),
                    "total_coverage_exposure": float(total_coverage)
                }
            })
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error getting company dashboard stats: {e}")
        return json.dumps({"status": "error", "message": str(e)})
