"""
Models package.
"""
from app.core.database import Base
from app.models.company import Company
from app.models.policy_service import PolicyService
from app.models.user import User
from app.models.client import Client
from app.models.policy_type import PolicyType
from app.models.quote import Quote
from app.models.policy import Policy
from app.models.policy_template import PolicyTemplate
from app.models.payment import Payment, PaymentTransaction
from app.models.premium_schedule import PremiumSchedule
from app.models.endorsement import Endorsement
from app.models.notification import Notification
from app.models.api_keys import ApiKey
from app.models.rbac import Role, Permission, role_permissions
from app.models.settings import Settings

from app.models.inter_company_share import InterCompanyShare
from app.models.ticket import Ticket
from app.models.referral import Referral
from app.models.loyalty import LoyaltyPoint
from app.models.telematics import TelematicsData
from app.models.ml_model import MLModel
from app.models.document import Document
from app.models.document_template import DocumentTemplate
from app.models.claim import Claim
from app.models.claim_activity import ClaimActivity
from app.models.co_insurance import CoInsuranceShare
from app.models.share_code import ShareCode
from app.models.system_settings import SystemSettings, AiUsageLog
from app.models.client_details import ClientAutomobile, ClientHousing, ClientHealth, ClientLife, ClientDriver
from app.models.agent_memory import AgentMemory
from app.models.pos_location import POSLocation
from app.models.commission import Commission
from app.models.pos_inventory import POSInventory
from app.models.employee import EmployeeProfile
from app.models.payroll import PayrollTransaction
from app.models.ledger import Account, JournalEntry, LedgerEntry
from app.models.premium_policy import PremiumPolicyCriteria, PremiumPolicyType
from app.models.underwriting import Vehicle, Driver, DriverClaimHistory, DriverConvictionHistory, VehicleRiskProfile, UnderwritingRuleSet, UnderwritingRule, UnderwritingDecision, QuoteUnderwritingSnapshot
from app.models.product_catalog import InsuranceProduct, ProductVersion, CoverageDefinition, CoverageOption, RatingFactor, ProductUnderwritingRule, QuoteWizardSchema
from app.models.quote_element import QuoteElement
from app.models.sales import SalesTransaction, SalesTarget
from app.models.task import Task
from app.models.chat import ChatChannel, ChatMessage, ChatChannelMember
from app.models.help_guide import HelpGuide, GuideCompletion, GuideAccess, OnboardingStatus, GuideType, GuideSection

__all__ = [
    "Base",
    "Company", 
    "User", 
    "Client", 
    "PolicyType", 
    "Quote", 
    "Policy",
    "PolicyTemplate",
    "Payment",
    "PaymentTransaction",
    "PremiumSchedule",
    "Endorsement",
    "Notification",
    "ApiKey",
    "Role",
    "Permission",
    "role_permissions",
    "Settings",
    "InterCompanyShare",
    "Ticket",
    "Referral",
    "LoyaltyPoint",
    "TelematicsData",
    "MLModel",
    "Document", 
    "DocumentTemplate",
    "Claim", 
    "ClaimActivity",
    "CoInsuranceShare",
    "ShareCode",
    "SystemSettings",
    "AiUsageLog",
    "ClientAutomobile",
    "ClientDriver",
    "ClientHousing",
    "ClientHealth",
    "ClientLife",
    "AgentMemory",
    "POSLocation",
    "Commission",
    "POSInventory",
    "EmployeeProfile",
    "PayrollTransaction",
    "Account",
    "JournalEntry",
    "LedgerEntry",
    "PremiumPolicyCriteria",
    "PremiumPolicyType",
    "Vehicle",
    "Driver",
    "DriverClaimHistory",
    "DriverConvictionHistory",
    "VehicleRiskProfile",
    "UnderwritingRuleSet",
    "UnderwritingRule",
    "UnderwritingDecision",
    "QuoteUnderwritingSnapshot",
    "InsuranceProduct",
    "ProductVersion",
    "CoverageDefinition",
    "CoverageOption",
    "RatingFactor",
    "ProductUnderwritingRule",
    "QuoteWizardSchema",
    "PolicyService",
    "QuoteElement",
    "SalesTransaction",
    "SalesTarget",
    "Task",
    "ChatChannel",
    "ChatMessage",
    "ChatChannelMember",
    "HelpGuide",
    "GuideCompletion",
    "GuideAccess",
    "OnboardingStatus",
    "GuideType",
    "GuideSection",
]
