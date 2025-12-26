"""
API v1 router.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, 
    clients, 
    admin,
    policy_templates,
    quotes,
    policies,
    payments,
    financial_reports,
    policy_types,
    claims,
    portal,
    api_keys,
    permissions,
    settings,
    inter_company_shares,
    tickets,
    referrals,
    loyalty,
    telematics,
    ml_models,
    documents,
    users,
    share_code,
    companies,
    validation,
    dev,
    qr_verification,
    co_insurance,
    subscription,
    pos,
    sales_reports,
    employees,
    payroll,
    commissions,
    accounting,
    analytics,
    notifications,
    kyc,
    premium_policies,
    reinsurance,
    regulatory,
    underwriting,
    recovery
)

api_router = APIRouter()



# Include endpoint routers
api_router.include_router(dev.router, prefix="/dev", tags=["Development"])
api_router.include_router(qr_verification.router, prefix="/public/verify", tags=["Public Verification"])
api_router.include_router(co_insurance.router, prefix="/co-insurance", tags=["Co-insurance"])
api_router.include_router(pos.router, prefix="/pos", tags=["Point of Sale & Inventory"])
api_router.include_router(sales_reports.router, prefix="/sales-reports", tags=["Sales Analytics"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(policy_templates.router, prefix="/policy-templates", tags=["Policy Templates"])
api_router.include_router(quotes.router, prefix="/quotes", tags=["Quotes"])
api_router.include_router(policies.router, prefix="/policies", tags=["Policies"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(financial_reports.router, prefix="/reports", tags=["Financial Reports"])
api_router.include_router(policy_types.router, prefix="/policy-types", tags=["Policy Types"])
api_router.include_router(claims.router, prefix="/claims", tags=["Claims"])
api_router.include_router(portal.router, prefix="/portal", tags=["Client Portal"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["API Keys"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["Permissions"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
api_router.include_router(inter_company_shares.router, prefix="/inter-company", tags=["Inter-Company"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
api_router.include_router(referrals.router, prefix="/referrals", tags=["Referrals"])
api_router.include_router(loyalty.router, prefix="/loyalty", tags=["Loyalty"])
api_router.include_router(telematics.router, prefix="/telematics", tags=["Telematics"])
api_router.include_router(ml_models.router, prefix="/ml-models", tags=["ML Models"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(share_code.router, prefix="/share-codes", tags=["Share Code"])
api_router.include_router(companies.router, prefix="/companies", tags=["Companies"])
api_router.include_router(validation.router, prefix="/validation", tags=["Validation"])
api_router.include_router(subscription.router, prefix="/subscription", tags=["Subscription & AI AI Quotas"])

api_router.include_router(employees.router, prefix="/employees", tags=["Employees"])
api_router.include_router(payroll.router, prefix="/payroll", tags=["Payroll"])
api_router.include_router(commissions.router, prefix="/commissions", tags=["Commissions"])
api_router.include_router(accounting.router, prefix="/accounting", tags=["Accounting"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(kyc.router, prefix="/kyc", tags=["KYC & Digital Identity"])
api_router.include_router(premium_policies.router, prefix="/premium-policies", tags=["Premium Policies"])
api_router.include_router(reinsurance.router, prefix="/reinsurance", tags=["Reinsurance Management"])
api_router.include_router(regulatory.router, prefix="/regulatory", tags=["Regulatory & Compliance"])
api_router.include_router(underwriting.router, prefix="/underwriting", tags=["Underwriting Management"])
api_router.include_router(recovery.router, prefix="/recovery", tags=["Claims Recovery"])
