"""
Payment service for payment processing.
"""
from typing import Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
import random

from app.models.payment import Payment, PaymentTransaction
from app.models.co_insurance import CoInsuranceShare
from app.models.inter_company_share import InterCompanyShare
from app.repositories.payment_repository import PaymentRepository
from app.repositories.commission_repository import CommissionRepository
from app.services.commission_service import CommissionService
from app.services.payment_gateway_api import PaymentGatewayAPI
from app.models.company import Company


class PaymentService:
    """Service for payment processing."""
    
    def __init__(self, db: Session, payment_repo: PaymentRepository):
        self.db = db
        self.payment_repo = payment_repo
        from app.services.accounting_service import AccountingService
        self.accounting_service = AccountingService(db)
    
    def generate_payment_number(self, company_id: UUID) -> str:
        """Generate unique payment number."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = random.randint(1000, 9999)
        return f"PAY-{timestamp}-{random_suffix}"
    
    def create_payment(
        self,
        company_id: UUID,
        policy_id: UUID,
        client_id: UUID,
        amount: Decimal,
        payment_method: str,
        payment_gateway: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Payment:
        """Create a new payment record."""
        payment_number = self.generate_payment_number(company_id)
        
        payment = Payment(
            company_id=company_id,
            policy_id=policy_id,
            client_id=client_id,
            payment_number=payment_number,
            amount=amount,
            currency='XOF',
            payment_method=payment_method,
            payment_gateway=payment_gateway,
            status='pending',
            payment_metadata=metadata or {}
        )
        
        return self.payment_repo.create(payment)
    
    def process_payment(
        self,
        payment_id: UUID,
        payment_details: Dict[str, Any]
    ) -> Payment:
        """Process a payment through the appropriate gateway."""
        payment = self.payment_repo.get_by_id(payment_id)
        
        if not payment:
            raise ValueError("Payment not found")
        
        # Update status to processing
        payment.status = 'processing'
        self.payment_repo.update(payment)
        
        # In real implementation, this would call the appropriate payment gateway
        # For now, we'll simulate the payment
        
        try:
            if payment.payment_method == 'stripe':
                result = self._process_stripe_payment(payment, payment_details)
            elif payment.payment_method == 'mobile_money':
                result = self._process_mobile_money_payment(payment, payment_details)
            elif payment.payment_method == 'bank_transfer':
                result = self._process_bank_transfer(payment, payment_details)
            elif payment.payment_method == 'cash':
                result = self._process_cash_payment(payment, payment_details)
            else:
                raise ValueError(f"Unsupported payment method: {payment.payment_method}")
            
            # Create transaction record
            transaction = PaymentTransaction(
                payment_id=payment.id,
                transaction_id=result.get('transaction_id', f"TXN-{datetime.now().timestamp()}"),
                gateway=payment.payment_gateway or payment.payment_method,
                amount=payment.amount,
                currency=payment.currency,
                status=result.get('status', 'success'),
                gateway_response=result
            )
            self.payment_repo.create_transaction(transaction)
            
            if result.get('status') == 'success':
                payment.status = 'completed'
                payment.paid_at = datetime.utcnow()
                payment.reference_number = result.get('reference_number')
                
                # Check if this is a credit top-up
                if (payment.payment_metadata or {}).get('type') == 'ai_credits':
                    self._process_credit_topup(payment)
                else:
                    # Standard policy payment logic
                    self._generate_co_insurance_premium_shares(payment)
                    self._generate_commissions(payment)
                    self._post_payment_to_ledger(payment)
            elif result.get('status') == 'pending':
                payment.status = 'pending'
            else:
                payment.status = 'failed'
                payment.failure_reason = result.get('error_message', 'Payment processing failed')
            
            return self.payment_repo.update(payment)
            
        except Exception as e:
            payment.status = 'failed'
            payment.failure_reason = str(e)
            return self.payment_repo.update(payment)

    def _process_credit_topup(self, payment: Payment):
        """Update company AI credits after successful payment."""
        company = self.db.query(Company).filter(Company.id == payment.company_id).first()
        if company:
            credits_to_add = float(payment.amount)
            company.ai_credits_balance = (company.ai_credits_balance or 0.0) + credits_to_add
            self.db.add(company)
            # Ensure it's committed here so it's reflected immediately
            self.db.commit()
            print(f"Top-up processed: Added {credits_to_add} to {company.name}. New balance: {company.ai_credits_balance}")
            
            # 2. Notify User
            try:
                from app.services.notification_service import NotificationService
                notif_service = NotificationService(self.db)
                notif_service.send_topup_confirmation(
                    company_id=payment.company_id,
                    user_id=payment.created_by,
                    amount=float(payment.amount),
                    new_balance=company.ai_credits_balance,
                    payment_number=payment.payment_number
                )
            except Exception as e:
                print(f"Failed to send top-up notification: {e}")

    def _process_stripe_payment(self, payment: Payment, details: Dict[str, Any]) -> Dict[str, Any]:
        """Process Stripe payment using PaymentGatewayAPI."""
        if 'token' in details or 'payment_method_id' in details:
            return {
                'status': 'success',
                'transaction_id': f"ch_{datetime.now().timestamp()}",
                'reference_number': f"STRIPE-{payment.payment_number}",
                'gateway': 'stripe'
            }
        else:
            session = PaymentGatewayAPI.create_stripe_checkout_session(
                amount=payment.amount,
                currency=payment.currency,
                success_url=details.get('success_url', 'http://localhost:3000/success'),
                cancel_url=details.get('cancel_url', 'http://localhost:3000/cancel'),
                metadata={"payment_id": str(payment.id)}
            )
            return {
                'status': 'pending',
                'checkout_url': session['url'],
                'session_id': session['id'],
                'gateway': 'stripe'
            }
    
    def _process_mobile_money_payment(self, payment: Payment, details: Dict[str, Any]) -> Dict[str, Any]:
        """Process mobile money payment using PaymentGatewayAPI."""
        phone_number = details.get('phone_number')
        if not phone_number:
            raise ValueError("Phone number required for mobile money")
            
        result = PaymentGatewayAPI.initiate_mobile_money_payment(
            amount=payment.amount,
            currency=payment.currency,
            provider=payment.payment_gateway,
            phone_number=phone_number,
            external_id=str(payment.id)
        )
        
        return {
            'status': 'pending',
            'transaction_id': result.get('provider_reference'),
            'instructions': result.get('instructions'),
            'gateway': payment.payment_gateway,
            'reference_number': result.get('provider_reference')
        }
    
    def _post_payment_to_ledger(self, payment: Payment):
        """Post successful payment to general ledger."""
        try:
            from app.schemas.ledger import JournalEntryCreate, LedgerEntryCreate
            
            # 1. Initialize accounts if needed
            self.accounting_service.initialize_chart_of_accounts(payment.company_id)
            
            # 2. Get standard accounts
            cash_acc = self.accounting_service.get_or_create_account(payment.company_id, "1000", "Cash", "Asset")
            revenue_acc = self.accounting_service.get_or_create_account(payment.company_id, "4000", "Premium Income", "Revenue")
            
            # 3. Create Balanced Entry
            description = f"AI credit purchase"
            if payment.policy:
                description = f"Premium payment received for Policy {payment.policy.policy_number}"
                
            entry_data = JournalEntryCreate(
                description=description,
                reference=str(payment.payment_number),
                entries=[
                    LedgerEntryCreate(account_id=cash_acc.id, debit=payment.amount, credit=Decimal('0')),
                    LedgerEntryCreate(account_id=revenue_acc.id, debit=Decimal('0'), credit=payment.amount)
                ]
            )
            
            # Standard user for automated postings or system ID
            creator_id = payment.created_by or payment.company.admin_id if hasattr(payment.company, 'admin_id') else None
            if not creator_id:
                # Fallback to a super admin or first user
                from app.models.user import User
                sys_user = self.db.query(User).filter(User.company_id == payment.company_id).first()
                creator_id = sys_user.id if sys_user else None

            if creator_id:
                self.accounting_service.post_journal_entry(payment.company_id, entry_data, creator_id)
                
        except Exception as e:
            # Log error but don't fail the payment process
            print(f"Failed to post payment to ledger: {str(e)}")

    def _process_bank_transfer(self, payment: Payment, details: Dict[str, Any]) -> Dict[str, Any]:
        """Process bank transfer payment."""
        return {
            'status': 'success',
            'transaction_id': f"BT-{datetime.now().timestamp()}",
            'reference_number': details.get('reference_number', f"BANK-{payment.payment_number}"),
            'gateway': 'bank_transfer'
        }
    
    def _process_cash_payment(self, payment: Payment, details: Dict[str, Any]) -> Dict[str, Any]:
        """Process cash payment."""
        return {
            'status': 'success',
            'transaction_id': f"CASH-{datetime.now().timestamp()}",
            'reference_number': f"CASH-{payment.payment_number}",
            'gateway': 'cash'
        }
    
    def refund_payment(
        self,
        payment_id: UUID,
        refund_amount: Decimal,
        reason: str
    ) -> Payment:
        """Process a payment refund."""
        payment = self.payment_repo.get_by_id(payment_id)
        
        if not payment or payment.status != 'completed':
            raise ValueError("Payment cannot be refunded")
        
        # In production, this would call the gateway's refund API
        payment.status = 'refunded'
        payment.refunded_at = datetime.utcnow()
        payment.metadata['refund_reason'] = reason
        payment.metadata['refund_amount'] = str(refund_amount)
        
        return self.payment_repo.update(payment)
    
    def  handle_webhook(
        self,
        gateway: str,
        payload: Dict[str, Any]
    ) -> Optional[Payment]:
        """Handle payment gateway webhooks."""
        # Extract transaction ID from payload
        transaction_id = payload.get('transaction_id')
        
        if not transaction_id:
            return None
        
        # Find transaction
        transaction = self.payment_repo.get_transaction_by_id(transaction_id)
        
        if not transaction:
            return None
        
        # Update payment status based on webhook
        status = payload.get('status')
        payment = self.payment_repo.get_by_id(transaction.payment_id)
        
        if status == 'completed' or status == 'success':
            payment.status = 'completed'
            payment.paid_at = datetime.utcnow()
        elif status == 'failed':
            payment.status = 'failed'
            payment.failure_reason = payload.get('error_message')
        
        return self.payment_repo.update(payment)

    def _generate_co_insurance_premium_shares(self, payment: Payment):
        """Generate inter-company records for co-insurance premium distribution."""
        db = self.payment_repo.db # Assuming repository has db session
        
        # 1. Get co-insurance shares for the policy
        shares = db.query(CoInsuranceShare).filter(CoInsuranceShare.policy_id == payment.policy_id).all()
        
        if not shares:
            return

        for share in shares:
            # 2. Calculate participant's share of the premium
            # Participant gets their share % of the premium
            share_amount = (payment.amount * share.share_percentage) / 100
            
            # Management fee adjustment: if lead insurer keeps a fee, deduct it from participant's share
            if share.fee_percentage > 0:
                fee_amount = (share_amount * share.fee_percentage) / 100
                share_amount -= fee_amount
            
            # 3. Create inter-company share entry
            settlement = InterCompanyShare(
                from_company_id=payment.company_id, # Lead insurer (paying out share)
                to_company_id=share.company_id,     # Participant insurer (receiving share)
                resource_type="premium_distribution",
                resource_id=payment.id,
                amount=share_amount,
                currency=payment.currency,
                access_level="read",
                notes=f"Premium share ({share.share_percentage}%) for payment {payment.payment_number}. Fee: {share.fee_percentage}%"
            )
            db.add(settlement)
        
        db.commit()

    def _generate_commissions(self, payment: Payment):
        """Generate commission records for sales agents."""
        db = self.payment_repo.db
        
        # Get policy to find business source
        from app.repositories.policy_repository import PolicyRepository
        policy_repo = PolicyRepository(db)
        policy = policy_repo.get_by_id(payment.policy_id)
        
        if not policy:
            return

        # Initialize commission service
        comm_repo = CommissionRepository(db)
        comm_service = CommissionService(comm_repo)
        
        # Calculate and create commission
        comm_service.calculate_and_create_commission(policy, payment.amount)
