import os
import sys
import uuid
import json
import logging
from google.adk.tools import tool
from datetime import datetime

logger = logging.getLogger(__name__)

def _get_backend_root():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if root not in sys.path:
        sys.path.append(root)
    return root


@tool
def list_draft_quotes(company_id: str) -> str:
    """
    Lists all quotes with status 'draft', 'accepted', or 'sent' that can be converted into policies.
    Returns a list of quotes with their details.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.quote import Quote
        from sqlalchemy.orm import joinedload

        db = SessionLocal()
        try:
            quotes = db.query(Quote).options(
                joinedload(Quote.policy_type)
            ).filter(
                Quote.company_id == uuid.UUID(company_id),
                Quote.status.in_(['draft', 'accepted', 'sent'])
            ).order_by(Quote.created_at.desc()).limit(20).all()

            result = [{
                "id": str(q.id),
                "quote_number": q.quote_number,
                "client_name": q.client_name,
                "policy_type": q.policy_type.name if q.policy_type else "General",
                "coverage_amount": float(q.coverage_amount) if q.coverage_amount else 0,
                "final_premium": float(q.final_premium) if q.final_premium else 0,
                "status": q.status,
                "created_at": q.created_at.strftime("%Y-%m-%d") if q.created_at else ""
            } for q in quotes]

            return json.dumps({"status": "success", "quotes": result, "count": len(result)})
        finally:
            db.close()
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@tool
def convert_quote_to_policy(quote_id: str, company_id: str, user_id: str, start_date: str = None) -> str:
    """
    Prepares a deterministic handoff for converting an accepted quote into an active insurance policy.
    The AI layer may explain readiness but must not bind/issue the policy directly.
    """
    _get_backend_root()
    try:
        from app.services.ai_action_control_service import AiActionControlService, RestrictedInsuranceOperation

        return AiActionControlService().restricted_response_json(
            RestrictedInsuranceOperation.BIND_POLICY,
            requested_by="policy_agent.convert_quote_to_policy",
            record_reference=quote_id,
            next_step="Use the deterministic policy lifecycle workflow to issue the policy after authorization and audit checks."
        )
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@tool
def list_active_policies(company_id: str, client_id: str = None) -> str:
    """
    Lists active policies for a company, optionally filtered by client.
    Returns policy details including status, dates, and premium amounts.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.policy import Policy
        from sqlalchemy.orm import joinedload

        db = SessionLocal()
        try:
            query = db.query(Policy).options(
                joinedload(Policy.client),
                joinedload(Policy.policy_type)
            ).filter(Policy.company_id == uuid.UUID(company_id))

            if client_id:
                query = query.filter(Policy.client_id == uuid.UUID(client_id))

            policies = query.order_by(Policy.created_at.desc()).limit(20).all()

            result = [{
                "id": str(p.id),
                "policy_number": p.policy_number,
                "client_name": f"{p.client.first_name} {p.client.last_name}" if p.client else "Unknown",
                "policy_type": p.policy_type.name if p.policy_type else "General",
                "premium_amount": float(p.premium_amount) if p.premium_amount else 0,
                "coverage_amount": float(p.coverage_amount) if p.coverage_amount else 0,
                "start_date": p.start_date.isoformat() if p.start_date else "",
                "end_date": p.end_date.isoformat() if p.end_date else "",
                "status": p.status,
                "days_until_expiry": p.days_until_expiry if hasattr(p, 'days_until_expiry') else 0
            } for p in policies]

            return json.dumps({"status": "success", "policies": result, "count": len(result)})
        finally:
            db.close()
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@tool
def get_policy_details(policy_number: str, company_id: str) -> str:
    """
    Gets detailed information about a specific policy including its services and claims.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.policy import Policy
        from sqlalchemy.orm import joinedload

        db = SessionLocal()
        try:
            policy = db.query(Policy).options(
                joinedload(Policy.client),
                joinedload(Policy.policy_type),
                joinedload(Policy.services),
                joinedload(Policy.claims)
            ).filter(
                Policy.company_id == uuid.UUID(company_id),
                Policy.policy_number == policy_number
            ).first()

            if not policy:
                return json.dumps({"status": "error", "message": f"Policy '{policy_number}' not found."})

            claims_data = [{
                "claim_number": c.claim_number,
                "status": c.status,
                "incident_date": c.incident_date.isoformat() if c.incident_date else ""
            } for c in (policy.claims or [])]

            services_data = [{
                "name": s.name_en if hasattr(s, 'name_en') else s.name,
                "price": float(s.default_price) if hasattr(s, 'default_price') and s.default_price else 0
            } for s in (policy.services or [])]

            return json.dumps({
                "status": "success",
                "policy": {
                    "policy_number": policy.policy_number,
                    "client_name": f"{policy.client.first_name} {policy.client.last_name}" if policy.client else "Unknown",
                    "policy_type": policy.policy_type.name if policy.policy_type else "General",
                    "premium_amount": float(policy.premium_amount) if policy.premium_amount else 0,
                    "coverage_amount": float(policy.coverage_amount) if policy.coverage_amount else 0,
                    "start_date": policy.start_date.isoformat() if policy.start_date else "",
                    "end_date": policy.end_date.isoformat() if policy.end_date else "",
                    "status": policy.status,
                    "auto_renew": policy.auto_renew if hasattr(policy, 'auto_renew') else False,
                    "days_until_expiry": policy.days_until_expiry if hasattr(policy, 'days_until_expiry') else 0,
                    "claims": claims_data,
                    "services": services_data
                }
            })
        finally:
            db.close()
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@tool
def cancel_policy(policy_number: str, company_id: str, reason: str) -> str:
    """
    Prepares a deterministic handoff for policy cancellation.
    The AI layer may collect the reason and explain the process but must not cancel the policy directly.
    """
    _get_backend_root()
    try:
        from app.services.ai_action_control_service import AiActionControlService, RestrictedInsuranceOperation

        return AiActionControlService().restricted_response_json(
            RestrictedInsuranceOperation.CANCEL_POLICY,
            requested_by="policy_agent.cancel_policy",
            record_reference=policy_number,
            next_step="Create a cancellation request for the deterministic policy lifecycle workflow instead of changing policy status from the AI tool."
        )
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
