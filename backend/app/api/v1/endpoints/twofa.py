"""
Two-Factor Authentication (2FA) endpoints.

Routes
------
POST /2fa/setup          – Begin TOTP enrollment (returns secret + QR code)
POST /2fa/verify-setup   – Confirm enrollment with a TOTP code and activate 2FA
POST /2fa/disable        – Disable 2FA (requires current TOTP or backup code)
POST /2fa/verify         – Verify a TOTP code during login
POST /2fa/backup-codes   – Regenerate backup codes
POST /2fa/sms/send       – Send SMS OTP (fallback)
POST /2fa/sms/verify     – Verify SMS OTP
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.twofa_service import TwoFAService
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


# ── Request / Response Models ─────────────────────────────────────────────────

class TOTPSetupResponse(BaseModel):
    secret: str
    totp_uri: str
    qr_code: Optional[str]
    backup_codes: List[str]
    message: str

class VerifyCodeRequest(BaseModel):
    code: str

class SMSRequest(BaseModel):
    phone_number: Optional[str] = None  # override; defaults to user's phone

class VerifyResponse(BaseModel):
    success: bool
    message: str


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_user_totp_secret(user: User) -> Optional[str]:
    return getattr(user, "mfa_secret", None)

def _get_user_backup_hashes(user: User) -> List[str]:
    import json
    raw = getattr(user, "backup_codes", None)
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, Exception):
            pass
    return []

def _user_has_2fa(user: User) -> bool:
    return bool(getattr(user, "mfa_enabled", False))


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/setup", response_model=TOTPSetupResponse)
def setup_2fa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Initiate TOTP 2FA enrollment.
    Returns the TOTP secret, QR code data URI, and one-time backup codes.
    2FA is NOT yet active until /verify-setup is called with a valid code.
    """
    result = TwoFAService.setup_totp_for_user(current_user.email)

    # Persist secret and backup code hashes (but NOT enabled yet)
    try:
        import json
        current_user.mfa_secret = result["secret"]
        # Store hashed backup codes as JSON string
        current_user.backup_codes = json.dumps(result["hashed_backup_codes"])
        db.commit()
    except Exception as e:
        logger.error(f"2FA setup DB save failed for user {current_user.id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save 2FA secret. Please try again.",
        )

    return TOTPSetupResponse(
        secret=result["secret"],
        totp_uri=result["totp_uri"],
        qr_code=result["qr_code"],
        backup_codes=result["backup_codes"],
        message=(
            "Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.), "
            "then call /2fa/verify-setup with a valid code to activate 2FA. "
            "Save your backup codes in a safe place — they will not be shown again."
        ),
    )


@router.post("/verify-setup", response_model=VerifyResponse)
def verify_2fa_setup(
    body: VerifyCodeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Complete TOTP 2FA enrollment by verifying the first code from the authenticator app.
    """
    secret = _get_user_totp_secret(current_user)
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA setup not initiated. Call /2fa/setup first.",
        )

    if not TwoFAService.verify_totp(secret, body.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid TOTP code. Please check your authenticator app and try again.",
        )

    try:
        current_user.mfa_enabled = True
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    return VerifyResponse(success=True, message="Two-factor authentication is now enabled.")


@router.post("/verify", response_model=VerifyResponse)
def verify_2fa(
    body: VerifyCodeRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Verify a TOTP code (called during login when 2FA is enabled).
    Also accepts a backup code (8 characters).
    """
    if not _user_has_2fa(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled for this account.",
        )

    code = body.code.strip()
    secret = _get_user_totp_secret(current_user)

    if len(code) == 6 and code.isdigit():
        # Standard TOTP
        if TwoFAService.verify_totp(secret or "", code):
            return VerifyResponse(success=True, message="TOTP verification successful.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired TOTP code.",
        )

    # Treat as backup code
    stored_hashes = _get_user_backup_hashes(current_user)
    valid, remaining = TwoFAService.verify_and_consume_backup_code(code, stored_hashes)
    if valid:
        try:
            import json
            current_user.backup_codes = json.dumps(remaining)
            from app.core.database import SessionLocal
            db = SessionLocal()
            db.add(current_user)
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to consume backup code for user {current_user.id}: {e}")
        return VerifyResponse(
            success=True,
            message=f"Backup code accepted. {len(remaining)} backup codes remaining.",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid code.",
    )


@router.post("/disable", response_model=VerifyResponse)
def disable_2fa(
    body: VerifyCodeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Disable 2FA. Requires a valid TOTP code or backup code to confirm."""
    if not _user_has_2fa(current_user):
        raise HTTPException(status_code=400, detail="2FA is not enabled.")

    code = body.code.strip()
    secret = _get_user_totp_secret(current_user)
    verified = False

    if len(code) == 6 and code.isdigit():
        verified = TwoFAService.verify_totp(secret or "", code)
    else:
        stored_hashes = _get_user_backup_hashes(current_user)
        verified, _ = TwoFAService.verify_and_consume_backup_code(code, stored_hashes)

    if not verified:
        raise HTTPException(status_code=401, detail="Invalid code. 2FA not disabled.")

    try:
        import json
        current_user.mfa_enabled = False
        current_user.mfa_secret = None
        current_user.backup_codes = json.dumps([])
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    return VerifyResponse(success=True, message="Two-factor authentication has been disabled.")


@router.post("/backup-codes", response_model=dict)
def regenerate_backup_codes(
    body: VerifyCodeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Regenerate backup codes. Requires TOTP verification to prevent misuse.
    Returns the new plain codes (shown once only).
    """
    if not _user_has_2fa(current_user):
        raise HTTPException(status_code=400, detail="2FA is not enabled.")

    secret = _get_user_totp_secret(current_user)
    if not TwoFAService.verify_totp(secret or "", body.code):
        raise HTTPException(status_code=401, detail="Invalid TOTP code.")

    plain, hashed = TwoFAService.generate_and_hash_backup_codes()
    try:
        import json
        current_user.backup_codes = json.dumps(hashed)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    return {
        "backup_codes": plain,
        "message": "New backup codes generated. Save them in a safe place — they will not be shown again.",
    }


@router.post("/sms/send", response_model=VerifyResponse)
def send_sms_otp(
    body: SMSRequest,
    current_user: User = Depends(get_current_user),
):
    """Send an SMS OTP as a 2FA fallback."""
    phone = body.phone_number or getattr(current_user, "phone", None)
    if not phone:
        raise HTTPException(
            status_code=400,
            detail="No phone number on account. Provide phone_number in the request body.",
        )
    sent = TwoFAService.send_sms_otp(phone)
    if not sent:
        raise HTTPException(status_code=500, detail="Failed to send SMS OTP.")
    return VerifyResponse(success=True, message=f"OTP sent to {phone[:4]}***.")


@router.post("/sms/verify", response_model=VerifyResponse)
def verify_sms_otp(
    body: VerifyCodeRequest,
    current_user: User = Depends(get_current_user),
):
    """Verify an SMS OTP."""
    phone = getattr(current_user, "phone", None)
    if not phone:
        raise HTTPException(status_code=400, detail="No phone number on account.")
    if TwoFAService.verify_sms_otp(phone, body.code):
        return VerifyResponse(success=True, message="SMS OTP verified successfully.")
    raise HTTPException(status_code=401, detail="Invalid or expired SMS OTP.")
