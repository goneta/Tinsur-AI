"""
Quote service for business logic operations.
"""
from typing import Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date, timedelta
import random

from app.models.quote import Quote
from app.models.client import Client
from app.models.policy_type import PolicyType
from app.models.premium_policy import PremiumPolicyType, PremiumPolicyCriteria
from app.repositories.quote_repository import QuoteRepository
from app.services.underwriting_service import UnderwritingService
from app.models.company import Company
from app.models.user import User


class QuoteService:
    """Service for quote-related business logic."""
    
    def __init__(self, quote_repo: QuoteRepository):
        self.quote_repo = quote_repo
        self.underwriting_service = UnderwritingService(quote_repo.db)
    
    def generate_quote_number(self, company_id: UUID, policy_type_code: str) -> str:
        """Generate unique quote number."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = random.randint(1000, 9999)
        return f"Q-{policy_type_code}-{timestamp}-{random_suffix}"
    
    def calculate_premium(
        self,
        risk_factors: Dict[str, Any],
        duration_months: int = 12,
        policy_id: Optional[UUID] = None,
        company_id: Optional[UUID] = None,
        financial_overrides: Optional[Dict[str, Any]] = None,
        # Added missing args expected by endpoint
        policy_type_id: Optional[UUID] = None,
        coverage_amount: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Calculate premium based on policy type and risk factors.
        """
        # Initialize variables safely
        if coverage_amount is None:
            coverage_amount = Decimal('0')

        # Base premium rate (percentage of coverage)
        base_rates = {
            'VEHICLE': Decimal('0.05'),
            'PROPERTY': Decimal('0.03'),
            'LIFE': Decimal('0.02'),
            'HEALTH': Decimal('0.04'),
        }
        
        # Default coverage amount if not passed (Note: this logic looks flawed as coverage_amount is not in args, but keeping existing logic structure)
        # Assuming coverage_amount was intended to be passed or derived. 
        # Looking at original code: "base_premium = coverage_amount * base_rate" 
        # But coverage_amount is NOT defined in calculate_premium scope in the original file!
        # This is another bug. 
        # However, looking closely at original file line 52: "base_premium = coverage_amount * base_rate"
        # coverage_amount is undefined.
        # Wait, I cannot fix logic bugs I wasn't asked to fix, but this will crash.
        # But the user only asked to "start the servers".
        # The SyntaxError is the blocker.
        # I will assume coverage_amount is passed or global (unlikely).
        # Actually, let's look at where coverage_amount comes from. 
        # It is NOT in the arguments.
        # I should probably add coverage_amount to arguments or fix it.
        # But I should stick to fixing the SyntaxError first.
        # I'll comment it out or leave it to fail at runtime if that's what's there?
        # No, "NameError" will happen.
        # But wait, python scope... maybe it's a global? No.
        
        # Let's fix the SyntaxError first.
        
        # Handle overrides
        if financial_overrides and financial_overrides.get('base_rate') is not None:
            # Assuming base_rate is passed as percentage (e.g. 5.0)
            base_rate = Decimal(str(financial_overrides['base_rate'])) / Decimal('100')
        else:
            base_rate = base_rates.get('VEHICLE', Decimal('0.04'))
        # base_premium = coverage_amount * base_rate 
        # I will assume coverage_amount needs to be 0 or I'll break it more.
        # Replacing with usage of risk_factors.get('coverage_amount') maybe?
        
        if coverage_amount is not None:
             coverage_amount = Decimal(str(coverage_amount))
        else:
             coverage_amount = Decimal(str(risk_factors.get('coverage_amount', '10000')))

        # Define duration_factor BEFORE usage
        duration_factor = Decimal(duration_months) / Decimal(12)
        
        # Initialize apr_percent safely
        apr_percent = 0.0

        # Determine Base Premium
        base_premium = Decimal('0')
        
        # 1. Try to get price from Selected Policy
        if policy_type_id:
             policy = self.quote_repo.db.query(PremiumPolicyType).filter(PremiumPolicyType.id == policy_type_id).first()
             if policy and policy.price:
                 # Use Policy Fixed Price as Base
                 base_premium = Decimal(str(policy.price))
                 # Adjust for duration? Assuming policy price is Annual.
                 base_premium = base_premium * duration_factor
        
        # 2. Fallback to Coverage * Rate if no policy price or 0
        if base_premium == 0:
            base_premium = coverage_amount * base_rate
            base_premium = base_premium * duration_factor

        # Calculate risk adjustments (User Requirement: Additive Percentage Increases on Base)
        risk_score = self._calculate_risk_score(risk_factors)
        
        # Risk Score Cost (0-100 scale, treated as percentage add-on)
        # Assuming risk_score 50 is neutral? Or is it 0-100% add on? 
        # Previous logic: score_cost = adjusted_base * (score/100). 
        # We will treat score as a direct percentage add-on to Base.
        score_cost = base_premium * (risk_score / Decimal('100'))

        # Risk Multipliers (Explicit Financial Overrides)
        multiplier_cost = Decimal('0')
        if financial_overrides and 'risk_multiplier' in financial_overrides:
             multipliers = financial_overrides['risk_multiplier']
             if isinstance(multipliers, list):
                 for m in multipliers:
                     # Additive: (Multiplier - 1) * Base
                     # e.g. 1.25 -> 0.25 * Base
                     factor = Decimal(str(m)) - Decimal('1')
                     multiplier_cost += base_premium * factor
             else:
                 factor = Decimal(str(multipliers)) - Decimal('1')
                 multiplier_cost += base_premium * factor

        # Total Risk Adjustment
        total_risk_adjustment = multiplier_cost + score_cost

        # Discounts (User Requirement: Calculated on Base Premium)
        discount_percent = Decimal('0')
        if financial_overrides and 'company_discount' in financial_overrides:
            discounts = financial_overrides['company_discount']
            if isinstance(discounts, list):
                 for d in discounts:
                     discount_percent += Decimal(str(d))
            else:
                 discount_percent = Decimal(str(discounts))
        
        discount_amount = base_premium * (discount_percent / Decimal('100'))

        # UBI Adjustment (Placeholder for Phase 7)
        ubi_adjustment_amount = Decimal('0')

        # Fees (Fixed amounts)
        arrangement_fee = Decimal('0')
        extra_fee = Decimal('0')
        
        if company_id:
            company = self.quote_repo.db.query(Company).filter(Company.id == company_id).first()
            if company:
                apr_percent = company.apr_percent or 0.0
                arrangement_fee = Decimal(str(company.arrangement_fee or 0))
                extra_fee = Decimal(str(company.extra_fee or 0))

        if financial_overrides and 'fixed_fee' in financial_overrides:
            fees = financial_overrides['fixed_fee']
            if isinstance(fees, list):
                for f in fees:
                    extra_fee += Decimal(str(f))
            else:
                extra_fee += Decimal(str(fees))

        # Subtotal (Base - Discount + Risk + Fees)
        # User Formula: Subtotal = Base Premium - Total Discount + Total Risk Adjustment
        # (We append Fees to this as they are pre-tax generally, or we can make them post-tax.
        # User didn't specify Fees location, but usually fees are taxable or exempt. 
        # We will include them in Subtotal for Tax calculation unless specified otherwise)
        subtotal = base_premium - discount_amount + total_risk_adjustment + extra_fee

        # Tax (User Requirement: Subtotal * Tax Rate)
        tax_percent = Decimal('0')
        if financial_overrides and 'government_tax' in financial_overrides:
            taxes = financial_overrides['government_tax']
            if isinstance(taxes, list):
                for t in taxes:
                    tax_percent += Decimal(str(t))
            else:
                 tax_percent = Decimal(str(taxes))
        
        tax_amount = subtotal * (tax_percent / Decimal('100'))

        # Final Premium
        final_premium = subtotal + tax_amount

        # Total Financed
        total_financed_amount = final_premium + arrangement_fee
        
        interest_amount = total_financed_amount * (Decimal(str(apr_percent)) / Decimal('100'))
        total_installment_price = total_financed_amount + interest_amount
        
        monthly_installment = Decimal('0')
        if duration_months > 0:
            monthly_installment = total_installment_price / Decimal(duration_months)

        return {
            'base_premium': base_premium,
            'risk_adjustment': total_risk_adjustment,
            'ubi_adjustment': ubi_adjustment_amount,
            'risk_score': risk_score,
            'final_premium': final_premium,
            'premium_evaluation': self.evaluate_premium_policy(company_id, risk_factors) if company_id else None,
            'discount_amount': discount_amount if 'discount_amount' in locals() else Decimal('0'),
            'tax_amount': tax_amount if 'tax_amount' in locals() else Decimal('0'),
            'risk_factors_analysis': self._analyze_risk_factors(risk_factors),
            'recommendations': self._generate_recommendations(risk_score, risk_factors),
            # Financials
            'apr_percent': float(apr_percent),
            'arrangement_fee': arrangement_fee,
            'extra_fee': extra_fee,
            'total_financed_amount': total_financed_amount,
            'monthly_installment': monthly_installment,
            'total_installment_price': total_installment_price,
            'excess': Decimal('0'),
            'included_services': []
        }
        
        # Populate excess and services if premium evaluation exists
        if result['premium_evaluation']:
            result['excess'] = result['premium_evaluation'].get('excess', Decimal('0'))
            result['included_services'] = result['premium_evaluation'].get('included_services', [])
            
        return result
    
    def _calculate_risk_score(self, risk_factors: Dict[str, Any]) -> Decimal:
        """Calculate risk score from risk factors (0-100)."""
        score = Decimal('50')  # Base score
        
        # Example risk factor calculations for vehicle insurance
        if 'driver_age' in risk_factors:
            age = risk_factors['driver_age']
            if age < 25:
                score += Decimal('15')
            elif age > 60:
                score += Decimal('10')
            else:
                score -= Decimal('5')
        
        if 'accidents' in risk_factors:
            accidents = risk_factors.get('accidents', 0)
            score += Decimal(str(accidents * 10))
        
        if 'vehicle_age' in risk_factors:
            vehicle_age = risk_factors['vehicle_age']
            score += Decimal(str(vehicle_age * 2))
        
        # Ensure score is within 0-100
        return max(Decimal('0'), min(Decimal('100'), score))
    
    def _analyze_risk_factors(self, risk_factors: Dict[str, Any]) -> Dict[str, str]:
        """Analyze risk factors and provide insights."""
        analysis = {}
        
        if 'driver_age' in risk_factors:
            age = risk_factors['driver_age']
            if age < 25:
                analysis['driver_age'] = 'High risk: Young driver'
            elif age > 60:
                analysis['driver_age'] = 'Moderate risk: Senior driver'
            else:
                analysis['driver_age'] = 'Low risk: Experienced driver'
        
        if 'accidents' in risk_factors:
            accidents = risk_factors.get('accidents', 0)
            if accidents == 0:
                analysis['accidents'] = 'Excellent: No accident history'
            elif accidents <= 2:
                analysis['accidents'] = 'Moderate: Some accident history'
            else:
                analysis['accidents'] = 'High risk: Multiple accidents'
        
        return analysis
    
    def _generate_recommendations(self, risk_score: Decimal, risk_factors: Dict[str, Any]) -> list:
        """Generate recommendations based on risk profile."""
        recommendations = []
        
        if risk_score > 70:
            recommendations.append("Consider defensive driving course to reduce premium")
            recommendations.append("Install vehicle tracking device for potential discount")
        
        if risk_factors.get('accidents', 0) > 0:
            recommendations.append("Maintain clean driving record for better rates")
        
        return recommendations
    
    def create_quote(
        self,
        company_id: UUID,
        client_id: UUID,
        policy_type_id: UUID,
        coverage_amount: Decimal,
        risk_factors: Dict[str, Any],
        premium_frequency: str = 'annual',
        duration_months: int = 12,
        discount_percent: Decimal = Decimal('0'),
        created_by: UUID = None,
        pos_location_id: UUID = None,
        financial_overrides: Dict[str, Any] = None
    ) -> Quote:
        """Create a new quote with calculated premium."""
        # Fetch client data to ensure eligibility checks can run
        client = self.quote_repo.db.query(Client).filter(Client.id == client_id).first()
        client_data = {}
        if client:
             # Convert client model to dict safely
             client_data = {c.name: getattr(client, c.name) for c in client.__table__.columns}
        
        # Merge risk_factors with client data for eligibility checks
        # risk_factors take precedence if same key exists (though unlikely for base fields)
        full_risk_factors = {**client_data, **risk_factors}

        # Determine initial status
        initial_status = 'draft'
        if created_by:
            creator = self.quote_repo.db.query(User).filter(User.id == created_by).first()
            if creator and creator.role == 'client':
                initial_status = 'draft_from_client'
        
        calculation = self.calculate_premium(
            risk_factors=full_risk_factors,
            duration_months=duration_months,
            company_id=company_id,
            financial_overrides=financial_overrides,
            policy_type_id=policy_type_id,
            coverage_amount=coverage_amount
        )
        
        # Override discount_percent if company_discount is selected (for storage)
        if financial_overrides and 'company_discount' in financial_overrides:
            discounts = financial_overrides['company_discount']
            if isinstance(discounts, list):
                 for d in discounts:
                     discount_percent += Decimal(str(d))
            else:
                 discount_percent = Decimal(str(discounts))
        
        # Override premium_amount if a premium policy match was found
        if calculation.get('premium_evaluation'):
            premium_amount = Decimal(str(calculation['premium_evaluation']['price']))
            # If using fixed price policy, we might need to adjust final premium?
            # Current logic in calculate_premium doesn't seem to switch to fixed price.
            # It just returns 'premium_evaluation'.
            # If we strictly want to use the Calculated Final Premium:
            final_premium = calculation['final_premium']
        else:
            premium_amount = calculation['base_premium'] # Store base premium
            final_premium = calculation['final_premium']

        # Generate quote number
        quote_number = self.generate_quote_number(company_id, "AUTO")  # TODO: Get policy type code
        
        # Retrieve calculated values
        tax_amount = calculation['tax_amount']
        discount_amount = calculation['discount_amount']
        
        # Determine tax_percent (for storage)
        tax_percent = Decimal('0')
        if financial_overrides and 'government_tax' in financial_overrides:
             taxes = financial_overrides['government_tax']
             if isinstance(taxes, list):
                 for t in taxes:
                     tax_percent += Decimal(str(t))
             else:
                  tax_percent = Decimal(str(taxes))

        # Set validity (30 days from now)
        valid_until = date.today() + timedelta(days=30)
        
        # Create quote
        quote = Quote(
            company_id=company_id,
            client_id=client_id,
            policy_type_id=policy_type_id,
            quote_number=quote_number,
            coverage_amount=coverage_amount,
            premium_amount=premium_amount,
            discount_percent=discount_percent,
            tax_percent=tax_percent,
            tax_amount=tax_amount,
            final_premium=final_premium,
            premium_frequency=premium_frequency,
            duration_months=duration_months,
            risk_score=calculation['risk_score'],
            status=initial_status,
            valid_until=valid_until,
            details={**risk_factors, **(financial_overrides or {})},
            created_by=created_by,
            pos_location_id=pos_location_id,
            # Snapshot Financials
            apr_percent=calculation['apr_percent'],
            arrangement_fee=calculation['arrangement_fee'],
            extra_fee=calculation['extra_fee'],
            total_financed_amount=calculation['total_financed_amount'],
            monthly_installment=calculation['monthly_installment'],
            total_installment_price=calculation['total_installment_price'],
            # Premium Policy Snapshot
            excess=calculation.get('premium_evaluation', {}).get('excess', Decimal('0')),
            included_services=calculation.get('premium_evaluation', {}).get('included_services', [])
        )
        
        quote = self.quote_repo.create(quote)
        
        # Check Underwriting Authority
        if created_by:
            within_authority = self.underwriting_service.is_within_authority(created_by, coverage_amount)
            if not within_authority:
                self.underwriting_service.create_referral(
                    quote_id=quote.id,
                    referred_by_id=created_by,
                    reason=f"Coverage amount ({coverage_amount}) exceeds underwriting limit."
                )
                # Quote status is updated to 'referred' inside create_referral
        
        return quote
    
    def mark_as_sent(self, quote_id: UUID) -> Quote:
        """Mark quote as sent to client and trigger notification."""
        quote = self.quote_repo.get_by_id(quote_id)
        if quote:
            quote.status = 'sent'
            updated_quote = self.quote_repo.update(quote)
            
            # Send notification
            try:
                from app.services.notification_service import NotificationService
                # Assuming client relationship is loaded or accessible
                client_email = quote.client.email if quote.client else "customer@example.com"
                
                notif_service = NotificationService(self.quote_repo.db)
                notif_service.send_quote_notification(
                    company_id=quote.company_id,
                    client_id=quote.client_id,
                    client_email=client_email,
                    quote_number=quote.quote_number,
                    quote_pdf_url=f"/api/v1/quotes/{quote.id}/pdf" # Placeholder URL
                )
            except Exception as e:
                print(f"Failed to send quote notification: {e}")
                
            return updated_quote
        return None
    
    def accept_quote(self, quote_id: UUID) -> Quote:
        """Mark quote as accepted."""
        quote = self.quote_repo.get_by_id(quote_id)
        if quote and not quote.is_expired:
            quote.status = 'policy_created'
            return self.quote_repo.update(quote)
        return None
    
    def reject_quote(self, quote_id: UUID) -> Quote:
        """Mark quote as rejected."""
        quote = self.quote_repo.get_by_id(quote_id)
        if quote:
            quote.status = 'rejected'
            return self.quote_repo.update(quote)
        return None

    def archive_quote(self, quote_id: UUID) -> Quote:
        """Mark quote as archived."""
        quote = self.quote_repo.get_by_id(quote_id)
        if quote:
            quote.status = 'archived'
            return self.quote_repo.update(quote)
        return None
    
    def check_and_expire_quotes(self, company_id: UUID) -> int:
        """Check and mark expired quotes. Returns count of expired quotes."""
        expired_quotes = self.quote_repo.get_expired_quotes(company_id)
        count = 0
        for quote in expired_quotes:
            quote.status = 'expired'
            self.quote_repo.update(quote)
            count += 1
        return count

    def evaluate_premium_policy(self, company_id: UUID, client_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Evaluate client data against configured premium policy types.
        Returns the best matching premium policy type and its price.
        Raises exceptions for missing data or no configuration.
        """
        from fastapi import HTTPException, status
        
        db = self.quote_repo.db
        premium_types = db.query(PremiumPolicyType).filter(
            PremiumPolicyType.company_id == company_id,
            PremiumPolicyType.is_active == True
        ).all()

        if not premium_types:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "NO_PREMIUM_POLICIES",
                    "message": "There is no premium policy available. You must create a policy first before creating a quote."
                }
            )

        best_match = None
        missing_fields = set()
        
        for ptype in premium_types:
            all_criteria_met = True
            if not ptype.criteria:
                # If no criteria, it's a match/fallback? Assuming yes for now, or continue?
                # Usually policies without criteria might be defaults.
                # User request implies we must compare details.
                continue
                
            for criterion in ptype.criteria:
                # Check directly if value is missing before evaluating
                if client_data.get(criterion.field_name) is None:
                    missing_fields.add(criterion.field_name)
                    all_criteria_met = False
                    # Don't break immediately if we want to catch ALL missing fields for this policy
                    # But we can probably continue to next criterion
                    continue

                if not self._evaluate_criterion(criterion, client_data):
                    all_criteria_met = False
                    # Criteria mismatch (data present but wrong value) -> just this policy doesn't match
                    break
            
            if all_criteria_met and not missing_fields:
                best_match = {
                    "id": ptype.id,
                    "name": ptype.name,
                    "price": ptype.price,
                    "excess": ptype.excess,
                    "included_services": [s.name_en for s in ptype.services]
                }
                break
        
        # Priority:
        # 1. Successful match found -> Return it
        # 2. No match found, but fields were missing -> Raise "Missing Info"
        # 3. No match found, all data present -> Return None (standard "no match" logic, maybe fall back to base calc)
        
        if best_match:
            return best_match
            
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "MISSING_CLIENT_INFO",
                    "message": "Client information missing for eligibility check.",
                    "missing_fields": list(missing_fields)
                }
            )
            
        return None

    def _evaluate_criterion(self, criterion: PremiumPolicyCriteria, client_data: Dict[str, Any]) -> bool:
        """Evaluate a single criterion against client data. Assumes data exists."""
        val = client_data.get(criterion.field_name)
        # val check handled by caller now
            
        op = criterion.operator
        target = criterion.value
        
        try:
            if op == '=':
                return str(val) == str(target)
            elif op == '>':
                return float(val) > float(target)
            elif op == '<':
                return float(val) < float(target)
            elif op == '>=':
                return float(val) >= float(target)
            elif op == '<=':
                return float(val) <= float(target)
            elif op == 'between':
                low, high = map(float, target.split(','))
                return low <= float(val) <= high
        except (ValueError, TypeError):
            return False
            
        return False
