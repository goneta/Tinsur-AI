"""
Notification service for sending notifications.
Supports real SMTP email (smtplib / SMTP_SSL) and Twilio SMS.
Falls back to logging when credentials are not configured.
"""
import os
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.core.time import utcnow

logger = logging.getLogger(__name__)

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TwilioClient = None
    TWILIO_AVAILABLE = False

from app.models.notification import Notification


# ── helpers ──────────────────────────────────────────────────────────────────
def _smtp_cfg() -> Dict[str, str]:
    return {
        "host": os.getenv("SMTP_HOST", ""),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": os.getenv("SMTP_USER", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "from_email": os.getenv("SMTP_FROM_EMAIL", os.getenv("SMTP_USER", "noreply@tinsur.ai")),
        "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
    }

def _twilio_cfg() -> Dict[str, str]:
    return {
        "account_sid": os.getenv("TWILIO_ACCOUNT_SID", ""),
        "auth_token": os.getenv("TWILIO_AUTH_TOKEN", ""),
        "from_number": os.getenv("TWILIO_FROM_NUMBER", ""),
    }

def _smtp_configured() -> bool:
    cfg = _smtp_cfg()
    return bool(cfg["host"] and cfg["user"] and cfg["password"])

def _twilio_configured() -> bool:
    cfg = _twilio_cfg()
    return bool(cfg["account_sid"] and cfg["auth_token"] and cfg["from_number"])


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
        """Send email via SMTP. Falls back to logging when SMTP is not configured."""
        recipient = notification.recipient_email
        if not recipient:
            logger.warning("Email notification has no recipient_email; skipping.")
            return False

        if _smtp_configured():
            cfg = _smtp_cfg()
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = notification.subject or "Tinsur.AI Notification"
                msg["From"] = cfg["from_email"]
                msg["To"] = recipient
                msg.attach(MIMEText(notification.content or "", "plain", "utf-8"))

                if cfg["use_tls"]:
                    server = smtplib.SMTP(cfg["host"], cfg["port"])
                    server.starttls()
                else:
                    server = smtplib.SMTP_SSL(cfg["host"], int(cfg["port"]))
                server.login(cfg["user"], cfg["password"])
                server.sendmail(cfg["from_email"], [recipient], msg.as_string())
                server.quit()

                ext_id = f"smtp-{datetime.now().timestamp()}"
                logger.info(f"Email sent to {recipient} (subject: {notification.subject})")
            except Exception as e:
                logger.error(f"SMTP send failed to {recipient}: {e}")
                notification.status = "failed"
                notification.error_message = str(e)
                self.db.commit()
                return False
        else:
            logger.info(
                f"[SMTP not configured] Would send email to {recipient}: {notification.subject}"
            )
            ext_id = f"email-logged-{datetime.now().timestamp()}"

        notification.status = "sent"
        notification.sent_at = utcnow()
        notification.external_id = ext_id
        self.db.commit()
        return True

    def _send_sms(self, notification: Notification) -> bool:
        """Send SMS via Twilio. Falls back to logging when Twilio is not configured."""
        recipient = notification.recipient_phone
        if not recipient:
            logger.warning("SMS notification has no recipient_phone; skipping.")
            return False

        if TWILIO_AVAILABLE and _twilio_configured():
            cfg = _twilio_cfg()
            try:
                client = TwilioClient(cfg["account_sid"], cfg["auth_token"])
                message = client.messages.create(
                    body=notification.content or notification.subject or "Tinsur.AI notification",
                    from_=cfg["from_number"],
                    to=recipient,
                )
                ext_id = message.sid
                logger.info(f"SMS sent to {recipient} via Twilio (sid: {ext_id})")
            except Exception as e:
                logger.error(f"Twilio SMS failed to {recipient}: {e}")
                notification.status = "failed"
                notification.error_message = str(e)
                self.db.commit()
                return False
        else:
            logger.info(
                f"[Twilio not configured] Would send SMS to {recipient}: "
                f"{(notification.content or '')[:80]}"
            )
            ext_id = f"sms-logged-{datetime.now().timestamp()}"

        notification.status = "sent"
        notification.sent_at = utcnow()
        notification.external_id = ext_id
        self.db.commit()
        return True

    def _send_whatsapp(self, notification: Notification) -> bool:
        """Send WhatsApp via Twilio WhatsApp sandbox. Falls back to logging."""
        recipient = notification.recipient_phone
        if not recipient:
            logger.warning("WhatsApp notification has no recipient_phone; skipping.")
            return False

        if TWILIO_AVAILABLE and _twilio_configured():
            cfg = _twilio_cfg()
            try:
                client = TwilioClient(cfg["account_sid"], cfg["auth_token"])
                wa_from = f"whatsapp:{cfg['from_number']}"
                wa_to = f"whatsapp:{recipient}"
                message = client.messages.create(
                    body=notification.content or notification.subject or "Tinsur.AI notification",
                    from_=wa_from,
                    to=wa_to,
                )
                ext_id = message.sid
                logger.info(f"WhatsApp sent to {recipient} (sid: {ext_id})")
            except Exception as e:
                logger.error(f"WhatsApp send failed to {recipient}: {e}")
                notification.status = "failed"
                notification.error_message = str(e)
                self.db.commit()
                return False
        else:
            logger.info(
                f"[Twilio WhatsApp not configured] Would send WhatsApp to {recipient}"
            )
            ext_id = f"wa-logged-{datetime.now().timestamp()}"

        notification.status = "sent"
        notification.sent_at = utcnow()
        notification.external_id = ext_id
        self.db.commit()
        return True

    def _send_push(self, notification: Notification) -> bool:
        """Send push notification via Firebase (FCM). Falls back to logging."""
        # Firebase FCM would require firebase-admin SDK and device tokens.
        # Logs the notification for now; integrate FCM when device tokens are available.
        logger.info(
            f"[FCM push] Would send push to client_id={notification.client_id}: "
            f"{notification.subject}"
        )
        notification.status = "sent"
        notification.sent_at = utcnow()
        self.db.commit()
        return True
