"""
Two-Factor Authentication (2FA) service.
Implements TOTP (RFC 6238) using pyotp with QR code provisioning,
backup code generation, and SMS fallback via Twilio.
"""
import os
import io
import secrets
import hashlib
import hmac
import logging
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from uuid import UUID

import pyotp

logger = logging.getLogger(__name__)

try:
    import qrcode
    from qrcode.image.svg import SvgImage
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

try:
    from qrcode.image.pure import PyPNGImage
    QRCODE_PNG_AVAILABLE = True
except (ImportError, Exception):
    QRCODE_PNG_AVAILABLE = False

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TwilioClient = None
    TWILIO_AVAILABLE = False


ISSUER_NAME = os.getenv("APP_NAME", "Tinsur.AI")
BACKUP_CODE_COUNT = 8
BACKUP_CODE_LEN = 8  # characters per code
# SMS OTP validity
SMS_OTP_TTL_SECONDS = 300  # 5 minutes


def _generate_backup_codes() -> List[str]:
    """Generate N single-use backup codes."""
    return [secrets.token_hex(BACKUP_CODE_LEN // 2).upper() for _ in range(BACKUP_CODE_COUNT)]


def _hash_backup_code(code: str) -> str:
    """One-way hash a backup code for storage."""
    return hashlib.sha256(code.encode()).hexdigest()


class TwoFAService:
    """
    Handles TOTP provisioning, verification, backup codes, and SMS OTP fallback.

    User model must expose (or be patchable with):
        totp_secret: str | None
        totp_enabled: bool
        backup_codes: list[str]  – stored as SHA-256 hashes
    """

    # ── TOTP Setup ────────────────────────────────────────────────────────────

    @staticmethod
    def generate_totp_secret() -> str:
        """Generate a new base32 TOTP secret."""
        return pyotp.random_base32()

    @staticmethod
    def get_totp_uri(secret: str, user_email: str) -> str:
        """Return the otpauth:// URI for use in authenticator apps."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=user_email, issuer_name=ISSUER_NAME)

    @staticmethod
    def generate_qr_code_base64(secret: str, user_email: str) -> Optional[str]:
        """
        Generate a QR code PNG as a base64-encoded data URI.
        Returns None if qrcode / Pillow is not available.
        """
        if not QRCODE_AVAILABLE:
            logger.warning("qrcode library not available; cannot generate QR code.")
            return None

        uri = TwoFAService.get_totp_uri(secret, user_email)
        try:
            img = qrcode.make(uri)
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            import base64
            b64 = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{b64}"
        except Exception as e:
            logger.error(f"QR code generation failed: {e}")
            return None

    # ── TOTP Verification ─────────────────────────────────────────────────────

    @staticmethod
    def verify_totp(secret: str, code: str, valid_window: int = 1) -> bool:
        """
        Verify a 6-digit TOTP code.
        valid_window=1 allows ±30s clock drift (1 period either side).
        """
        if not secret or not code:
            return False
        totp = pyotp.TOTP(secret)
        return totp.verify(code.strip(), valid_window=valid_window)

    # ── Backup Codes ──────────────────────────────────────────────────────────

    @staticmethod
    def generate_and_hash_backup_codes() -> Tuple[List[str], List[str]]:
        """
        Returns (plain_codes, hashed_codes).
        Store hashed_codes; show plain_codes to the user once.
        """
        plain = _generate_backup_codes()
        hashed = [_hash_backup_code(c) for c in plain]
        return plain, hashed

    @staticmethod
    def verify_and_consume_backup_code(
        code: str,
        stored_hashes: List[str],
    ) -> Tuple[bool, List[str]]:
        """
        Verify a backup code against stored hashes and remove it (one-time use).
        Returns (is_valid, remaining_hashes).
        """
        code_hash = _hash_backup_code(code.upper().strip())
        if code_hash in stored_hashes:
            remaining = [h for h in stored_hashes if h != code_hash]
            return True, remaining
        return False, stored_hashes

    # ── SMS OTP Fallback ──────────────────────────────────────────────────────

    # In-memory store for SMS OTPs (use Redis in production)
    _sms_otp_store: dict = {}  # key: phone_number → {otp, expires_at}

    @classmethod
    def send_sms_otp(cls, phone_number: str) -> bool:
        """
        Generate and send a 6-digit SMS OTP via Twilio.
        Falls back to logging when Twilio is not configured.
        Returns True if sent (or logged) successfully.
        """
        otp = str(secrets.randbelow(900000) + 100000)  # 6-digit
        expires_at = datetime.utcnow() + timedelta(seconds=SMS_OTP_TTL_SECONDS)
        cls._sms_otp_store[phone_number] = {"otp": otp, "expires_at": expires_at}

        account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        from_number = os.getenv("TWILIO_FROM_NUMBER", "")
        body = f"Your Tinsur.AI verification code is: {otp}. Valid for 5 minutes."

        if TWILIO_AVAILABLE and account_sid and auth_token and from_number:
            try:
                client = TwilioClient(account_sid, auth_token)
                client.messages.create(body=body, from_=from_number, to=phone_number)
                logger.info(f"SMS OTP sent to {phone_number}")
                return True
            except Exception as e:
                logger.error(f"Twilio SMS OTP failed for {phone_number}: {e}")
                return False
        else:
            logger.info(
                f"[Twilio not configured] SMS OTP for {phone_number}: {otp} "
                f"(expires {expires_at.isoformat()})"
            )
            return True

    @classmethod
    def verify_sms_otp(cls, phone_number: str, otp: str) -> bool:
        """Verify an SMS OTP. Consumes it on success."""
        entry = cls._sms_otp_store.get(phone_number)
        if not entry:
            return False
        if datetime.utcnow() > entry["expires_at"]:
            cls._sms_otp_store.pop(phone_number, None)
            return False
        if hmac.compare_digest(entry["otp"], otp.strip()):
            cls._sms_otp_store.pop(phone_number, None)
            return True
        return False

    # ── High-Level Helpers ────────────────────────────────────────────────────

    @staticmethod
    def setup_totp_for_user(
        user_email: str,
    ) -> dict:
        """
        Generate a new TOTP secret + backup codes and return everything
        the endpoint needs to return to the client for enrollment.

        The caller is responsible for saving secret + hashed_backup_codes to the DB.
        """
        secret = TwoFAService.generate_totp_secret()
        plain_codes, hashed_codes = TwoFAService.generate_and_hash_backup_codes()
        qr_data_uri = TwoFAService.generate_qr_code_base64(secret, user_email)
        totp_uri = TwoFAService.get_totp_uri(secret, user_email)

        return {
            "secret": secret,
            "totp_uri": totp_uri,
            "qr_code": qr_data_uri,
            "backup_codes": plain_codes,          # Show once to the user
            "hashed_backup_codes": hashed_codes,  # Store in DB
        }
