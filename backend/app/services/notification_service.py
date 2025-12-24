"""
Notification service for sending notifications.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime


from app.models.notification import Notification


class NotificationService:
    """Service for notification management and delivery."""
    
    def __init__(self, db_session):
        # In production, this would initialize email/SMS/WhatsApp clients
        self.db = db_session
    
    def send_payment_reminder(
        self,
        company_id: UUID,
        client_id: UUID,
        client_email: str,
        client_phone: str,
        policy_number: str,
        amount: float,
        due_date: str,
        channels: List[str] = ['email']
    ) -> List[Notification]:
        """Send payment reminder notification."""
        notifications = []
        
        subject = f"Payment Reminder - Policy {policy_number}"
        content = f"""
        Dear Customer,
        
        This is a reminder that your premium payment of XOF {amount:,.2f} 
        for policy {policy_number} is due on {due_date}.
        
        Please make your payment before the due date to avoid late fees.
        
        Thank you for choosing our insurance services.
        """
        
        for channel in channels:
            notification = Notification(
                company_id=company_id,
                client_id=client_id,
                notification_type='payment_reminder',
                channel=channel,
                recipient_email=client_email if channel == 'email' else None,
                recipient_phone=client_phone if channel in ['sms', 'whatsapp'] else None,
                subject=subject,
                content=content.strip(),
                status='pending',
                metadata={
                    'policy_number': policy_number,
                    'amount': amount,
                    'due_date': due_date
                }
            )
            
            self.db.add(notification)
            notifications.append(notification)
        
        self.db.commit()
        
        # In production, send notifications asynchronously via Celery
        for notification in notifications:
            self._send_notification(notification)
        
        return notifications
    
    def send_quote_notification(
        self,
        company_id: UUID,
        client_id: UUID,
        client_email: str,
        quote_number: str,
        quote_pdf_url: str
    ) -> Notification:
        """Send quote to client."""
        content = f"""
        Dear Customer,
        
        Thank you for requesting an insurance quote. Please find your quote 
        {quote_number} attached.
        
        This quote is valid for 30 days. Please contact us if you have any questions.
        
        Best regards,
        Insurance Team
        """
        
        notification = Notification(
            company_id=company_id,
            client_id=client_id,
            notification_type='quote_sent',
            channel='email',
            recipient_email=client_email,
            subject=f"Your Insurance Quote - {quote_number}",
            content=content.strip(),
            status='pending',
            metadata={
                'quote_number': quote_number,
                'quote_pdf_url': quote_pdf_url
            }
        )
        
        self.db.add(notification)
        self.db.commit()
        
        self._send_notification(notification)
        
        return notification
    
    def send_topup_confirmation(
        self,
        company_id: UUID,
        user_id: UUID,
        amount: float,
        new_balance: float,
        payment_number: str
    ) -> Notification:
        """Send confirmation of successful credit top-up."""
        from app.models.user import User
        user = self.db.query(User).get(user_id)
        if not user:
            return None

        subject = "Digital Credits Top-up Successful"
        content = f"""
        Success! Your account has been credited with {amount:,.2f} credits.
        Reference: {payment_number}
        New Balance: {new_balance:,.2f}
        
        You can now continue using AI-powered features for claims and automation.
        """
        
        notification = Notification(
            company_id=company_id,
            user_id=user_id,
            notification_type='payment_received',
            channel='email',
            recipient_email=user.email,
            subject=subject,
            content=content.strip(),
            status='pending',
            notification_metadata={
                'payment_number': payment_number,
                'amount': amount,
                'new_balance': new_balance
            }
        )
        
        self.db.add(notification)
        self.db.commit()
        self._send_notification(notification)
        return notification

    def send_claim_assessment_alert(
        self,
        company_id: UUID,
        adjuster_id: UUID,
        claim_number: str,
        severity: str,
        estimate: float
    ) -> Notification:
        """Alert adjuster that AI damage assessment is complete."""
        from app.models.user import User
        user = self.db.query(User).get(adjuster_id)
        if not user:
            return None

        subject = f"AI Damage Assessment Ready: {claim_number}"
        content = f"""
        AI has completed the damage assessment for claim {claim_number}.
        
        Severity: {severity}
        Suggested Estimate: XOF {estimate:,.2f}
        
        Please review the details in the claims dashboard to finalize the approval.
        """
        
        notification = Notification(
            company_id=company_id,
            user_id=adjuster_id,
            notification_type='claim_assessment_ready',
            channel='email',
            recipient_email=user.email,
            subject=subject,
            content=content.strip(),
            status='pending',
            notification_metadata={
                'claim_number': claim_number,
                'severity': severity,
                'estimate': estimate
            }
        )
        
        self.db.add(notification)
        self.db.commit()
        self._send_notification(notification)
        return notification

    def send_low_balance_alert(
        self,
        company_id: UUID,
        balance: float
    ) -> List[Notification]:
        """Alert company admins about low credit balance."""
        from app.models.user import User
        admins = self.db.query(User).filter(
            User.company_id == company_id,
            User.role == 'admin' # Assuming Role field exists
        ).all()
        
        notifications = []
        subject = "ACTION REQUIRED: Low AI Credit Balance"
        content = f"""
        Your AI credit balance is low: {balance:,.2f} remaining.
        
        To prevent service interruption for AI-powered claims and policy automation, 
        please top up your account balance soon.
        """
        
        for admin in admins:
            notification = Notification(
                company_id=company_id,
                user_id=admin.id,
                notification_type='low_balance_alert',
                channel='email',
                recipient_email=admin.email,
                subject=subject,
                content=content.strip(),
                status='pending',
                notification_metadata={'current_balance': balance}
            )
            self.db.add(notification)
            notifications.append(notification)
        
        self.db.commit()
        for n in notifications:
            self._send_notification(n)
        return notifications

    def _send_notification(self, notification: Notification) -> bool:
        """Send notification via appropriate channel."""
        try:
            if notification.channel == 'email':
                return self._send_email(notification)
            elif notification.channel == 'sms':
                return self._send_sms(notification)
            elif notification.channel == 'whatsapp':
                return self._send_whatsapp(notification)
            elif notification.channel == 'push':
                return self._send_push(notification)
            return False
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            self.db.commit()
            return False
    
    def _send_email(self, notification: Notification) -> bool:
        """Send email notification. (Placeholder for actual email service)"""
        # In production, use SendGrid, AWS SES, or similar
        print(f"Sending email to {notification.recipient_email}: {notification.subject}")
        
        notification.status = 'sent'
        notification.sent_at = datetime.utcnow()
        notification.external_id = f"email-{datetime.now().timestamp()}"
        self.db.commit()
        
        return True
    
    def _send_sms(self, notification: Notification) -> bool:
        """Send SMS notification. (Placeholder for actual SMS service)"""
        # In production, use Twilio or similar
        print(f"Sending SMS to {notification.recipient_phone}")
        
        notification.status = 'sent'
        notification.sent_at = datetime.utcnow()
        notification.external_id = f"sms-{datetime.now().timestamp()}"
        self.db.commit()
        
        return True
    
    def _send_whatsapp(self, notification: Notification) -> bool:
        """Send WhatsApp notification. (Placeholder)"""
        # In production, use WhatsApp Business API
        print(f"Sending WhatsApp to {notification.recipient_phone}")
        
        notification.status = 'sent'
        notification.sent_at = datetime.utcnow()
        notification.external_id = f"wa-{datetime.now().timestamp()}"
        self.db.commit()
        
        return True
    
    def _send_push(self, notification: Notification) -> bool:
        """Send push notification. (Placeholder)"""
        # In production, use Firebase Cloud Messaging or similar
        notification.status = 'sent'
        notification.sent_at = datetime.utcnow()
        self.db.commit()
        
        return True
