import os
import sys
import uuid
import json
import logging
from google.adk.tools import tool
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def _get_backend_root():
    """Get the backend root directory and add it to sys.path."""
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if root not in sys.path:
        sys.path.append(root)
    return root


@tool
def get_financial_summary(company_id: str, period_days: int = 30) -> str:
    """
    Gets a financial summary for the company over the specified period.
    Includes total premiums collected, claims paid, net revenue, and policy counts.
    Default period is last 30 days.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.policy import Policy
        from app.models.claim import Claim
        from app.models.quote import Quote
        from app.core.time import utcnow
        from sqlalchemy import func

        db = SessionLocal()
        try:
            cid = uuid.UUID(company_id)
            cutoff = utcnow() - timedelta(days=period_days)

            # Premiums from new policies in period
            new_policies = db.query(
                func.count(Policy.id).label('count'),
                func.coalesce(func.sum(Policy.premium_amount), 0).label('total_premium'),
                func.coalesce(func.sum(Policy.coverage_amount), 0).label('total_coverage')
            ).filter(
                Policy.company_id == cid,
                Policy.created_at >= cutoff
            ).first()

            # Claims in period
            claims_data = db.query(
                func.count(Claim.id).label('count'),
                func.coalesce(func.sum(Claim.estimated_amount), 0).label('total_estimated'),
                func.coalesce(func.sum(Claim.approved_amount), 0).label('total_approved')
            ).filter(
                Claim.company_id == cid,
                Claim.created_at >= cutoff
            ).first()

            # Quotes in period
            quotes_count = db.query(func.count(Quote.id)).filter(
                Quote.company_id == cid,
                Quote.created_at >= cutoff
            ).scalar() or 0

            quotes_converted = db.query(func.count(Quote.id)).filter(
                Quote.company_id == cid,
                Quote.created_at >= cutoff,
                Quote.status == 'converted'
            ).scalar() or 0

            total_premium = float(new_policies.total_premium or 0)
            total_claims = float(claims_data.total_approved or 0)

            return json.dumps({
                "status": "success",
                "period_days": period_days,
                "summary": {
                    "new_policies": new_policies.count or 0,
                    "total_premium_collected": total_premium,
                    "total_coverage_issued": float(new_policies.total_coverage or 0),
                    "claims_filed": claims_data.count or 0,
                    "claims_total_estimated": float(claims_data.total_estimated or 0),
                    "claims_total_approved": total_claims,
                    "net_underwriting_result": total_premium - total_claims,
                    "loss_ratio": round(total_claims / total_premium * 100, 2) if total_premium > 0 else 0,
                    "quotes_generated": quotes_count,
                    "quotes_converted": quotes_converted,
                    "conversion_rate": round(quotes_converted / quotes_count * 100, 2) if quotes_count > 0 else 0
                }
            })
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error in get_financial_summary: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)})


@tool
def get_claims_analysis(company_id: str) -> str:
    """
    Provides a detailed claims analysis including status breakdown, average processing time,
    and top claim types. Useful for risk management reports.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.claim import Claim
        from sqlalchemy import func

        db = SessionLocal()
        try:
            cid = uuid.UUID(company_id)

            # Status breakdown
            status_counts = db.query(
                Claim.status,
                func.count(Claim.id).label('count'),
                func.coalesce(func.sum(Claim.estimated_amount), 0).label('total_amount')
            ).filter(
                Claim.company_id == cid
            ).group_by(Claim.status).all()

            status_breakdown = [{
                "status": s.status,
                "count": s.count,
                "total_amount": float(s.total_amount)
            } for s in status_counts]

            # Total claims
            total = db.query(func.count(Claim.id)).filter(Claim.company_id == cid).scalar() or 0

            # High fraud score claims
            high_risk = db.query(func.count(Claim.id)).filter(
                Claim.company_id == cid,
                Claim.fraud_score > 0.5
            ).scalar() or 0

            return json.dumps({
                "status": "success",
                "analysis": {
                    "total_claims": total,
                    "status_breakdown": status_breakdown,
                    "high_risk_claims": high_risk,
                    "fraud_flagged_percentage": round(high_risk / total * 100, 2) if total > 0 else 0
                }
            })
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error in get_claims_analysis: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)})


@tool
def get_client_portfolio_analysis(company_id: str, client_id: str = None) -> str:
    """
    Analyzes a client's insurance portfolio or the company's overall client portfolio.
    If client_id is provided, gives individual analysis. Otherwise, gives company-wide overview.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.policy import Policy
        from app.models.client import Client
        from app.models.claim import Claim
        from sqlalchemy import func

        db = SessionLocal()
        try:
            cid = uuid.UUID(company_id)

            if client_id:
                # Individual client analysis
                cl_id = uuid.UUID(client_id)
                client = db.query(Client).filter(Client.id == cl_id).first()
                if not client:
                    return json.dumps({"status": "error", "message": "Client not found"})

                policies = db.query(Policy).filter(
                    Policy.company_id == cid,
                    Policy.client_id == cl_id
                ).all()

                claims = db.query(Claim).filter(
                    Claim.company_id == cid,
                    Claim.client_id == cl_id
                ).all()

                total_premium = sum(float(p.premium_amount or 0) for p in policies)
                total_claims_amount = sum(float(c.estimated_amount or 0) for c in claims)
                active_count = sum(1 for p in policies if p.status == 'active')

                return json.dumps({
                    "status": "success",
                    "client_analysis": {
                        "client_name": f"{client.first_name} {client.last_name}",
                        "total_policies": len(policies),
                        "active_policies": active_count,
                        "total_premium_paid": total_premium,
                        "total_claims_filed": len(claims),
                        "total_claims_amount": total_claims_amount,
                        "profitability": total_premium - total_claims_amount,
                        "risk_profile": client.risk_profile or "standard"
                    }
                })
            else:
                # Company-wide portfolio analysis
                total_clients = db.query(func.count(Client.id)).filter(Client.company_id == cid).scalar() or 0

                clients_with_policies = db.query(func.count(func.distinct(Policy.client_id))).filter(
                    Policy.company_id == cid,
                    Policy.status == 'active'
                ).scalar() or 0

                avg_premium = db.query(func.avg(Policy.premium_amount)).filter(
                    Policy.company_id == cid,
                    Policy.status == 'active'
                ).scalar() or 0

                return json.dumps({
                    "status": "success",
                    "portfolio_analysis": {
                        "total_clients": total_clients,
                        "clients_with_active_policies": clients_with_policies,
                        "penetration_rate": round(clients_with_policies / total_clients * 100, 2) if total_clients > 0 else 0,
                        "average_premium": float(avg_premium)
                    }
                })
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error in get_client_portfolio_analysis: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)})


@tool
def get_ai_usage_report(company_id: str, period_days: int = 30) -> str:
    """
    Gets AI usage statistics for the company including credits consumed,
    top agents used, and usage trends.
    """
    _get_backend_root()
    try:
        from app.core.database import SessionLocal
        from app.models.system_settings import AiUsageLog
        from app.core.time import utcnow
        from sqlalchemy import func

        db = SessionLocal()
        try:
            cid = uuid.UUID(company_id)
            cutoff = utcnow() - timedelta(days=period_days)

            # Total usage
            total = db.query(
                func.count(AiUsageLog.id).label('interactions'),
                func.coalesce(func.sum(AiUsageLog.credits_consumed), 0).label('credits')
            ).filter(
                AiUsageLog.company_id == cid,
                AiUsageLog.created_at >= cutoff
            ).first()

            # By agent breakdown
            by_agent = db.query(
                AiUsageLog.agent_name,
                func.count(AiUsageLog.id).label('count'),
                func.coalesce(func.sum(AiUsageLog.credits_consumed), 0).label('credits')
            ).filter(
                AiUsageLog.company_id == cid,
                AiUsageLog.created_at >= cutoff
            ).group_by(AiUsageLog.agent_name).all()

            agent_breakdown = [{
                "agent": a.agent_name,
                "interactions": a.count,
                "credits": float(a.credits)
            } for a in by_agent]

            return json.dumps({
                "status": "success",
                "ai_usage": {
                    "period_days": period_days,
                    "total_interactions": total.interactions or 0,
                    "total_credits_consumed": float(total.credits or 0),
                    "by_agent": agent_breakdown
                }
            })
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error in get_ai_usage_report: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)})
