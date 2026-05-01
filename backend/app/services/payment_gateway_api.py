"""
Payment gateway API integration service.
Supports Stripe (card payments) and Mobile Money (Orange, MTN, Wave, Moov, Djamo).
"""
import os
import logging
import hmac
import hashlib
import json
from typing import Dict, Any, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Conditional imports – the app still starts if libraries are absent
# ---------------------------------------------------------------------------
try:
    import stripe as stripe_lib
    STRIPE_AVAILABLE = True
except ImportError:
    stripe_lib = None
    STRIPE_AVAILABLE = False

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    httpx = None
    HTTPX_AVAILABLE = False


class PaymentGatewayAPI:
    """Service to interact with external payment gateways (Stripe + Mobile Money)."""

    # -----------------------------------------------------------------------
    # Configuration helpers
    # -----------------------------------------------------------------------
    @staticmethod
    def _get_stripe_key() -> str:
        return os.getenv("STRIPE_SECRET_KEY", "")

    @staticmethod
    def _get_stripe_webhook_secret() -> str:
        return os.getenv("STRIPE_WEBHOOK_SECRET", "")

    @staticmethod
    def _get_mobile_money_config(provider: str) -> Dict[str, str]:
        """Return API base URL, key, and secret for a mobile money provider."""
        provider_upper = provider.upper().replace("_MONEY", "").replace("_", "")
        return {
            "base_url": os.getenv(f"{provider_upper}_API_URL", ""),
            "api_key": os.getenv(f"{provider_upper}_API_KEY", ""),
            "api_secret": os.getenv(f"{provider_upper}_API_SECRET", ""),
            "merchant_id": os.getenv(f"{provider_upper}_MERCHANT_ID", ""),
            "callback_url": os.getenv("PAYMENT_CALLBACK_URL", os.getenv("API_BASE_URL", "http://localhost:8000") + "/api/v1/payments/webhooks/mobile-money"),
        }

    @staticmethod
    def is_stripe_configured() -> bool:
        key = os.getenv("STRIPE_SECRET_KEY", "")
        return bool(key) and key.startswith("sk_")

    @staticmethod
    def is_mobile_money_configured(provider: str) -> bool:
        cfg = PaymentGatewayAPI._get_mobile_money_config(provider)
        return bool(cfg["api_key"]) and bool(cfg["base_url"])

    # -----------------------------------------------------------------------
    # STRIPE  – real integration with graceful fallback to simulation
    # -----------------------------------------------------------------------
    @staticmethod
    def create_stripe_payment_intent(
        amount: Decimal,
        currency: str = "xof",
        payment_method_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a Stripe PaymentIntent. Returns client_secret for frontend confirmation."""
        if STRIPE_AVAILABLE and PaymentGatewayAPI.is_stripe_configured():
            stripe_lib.api_key = PaymentGatewayAPI._get_stripe_key()
            try:
                intent_params: Dict[str, Any] = {
                    "amount": int(amount),  # XOF is zero-decimal currency
                    "currency": currency.lower(),
                    "metadata": metadata or {},
                    "automatic_payment_methods": {"enabled": True},
                }
                if payment_method_id:
                    intent_params["payment_method"] = payment_method_id
                    intent_params["confirm"] = True
                    intent_params["return_url"] = metadata.get("return_url", "http://localhost:3000/dashboard/payments") if metadata else "http://localhost:3000/dashboard/payments"
                if customer_id:
                    intent_params["customer"] = customer_id

                intent = stripe_lib.PaymentIntent.create(**intent_params)
                logger.info(f"Stripe PaymentIntent created: {intent.id}")
                return {
                    "status": "requires_confirmation" if not payment_method_id else intent.status,
                    "payment_intent_id": intent.id,
                    "client_secret": intent.client_secret,
                    "gateway": "stripe",
                }
            except stripe_lib.error.StripeError as e:
                logger.error(f"Stripe error: {e}")
                return {"status": "failed", "error_message": str(e), "gateway": "stripe"}
        else:
            # Simulation mode
            logger.warning("Stripe not configured – using simulation mode")
            sim_id = f"pi_sim_{os.urandom(8).hex()}"
            return {
                "status": "succeeded" if payment_method_id else "requires_confirmation",
                "payment_intent_id": sim_id,
                "client_secret": f"{sim_id}_secret_sim",
                "gateway": "stripe",
                "simulated": True,
            }

    @staticmethod
    def create_stripe_checkout_session(
        amount: Decimal,
        currency: str,
        success_url: str,
        cancel_url: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a Stripe Checkout Session (hosted payment page)."""
        if STRIPE_AVAILABLE and PaymentGatewayAPI.is_stripe_configured():
            stripe_lib.api_key = PaymentGatewayAPI._get_stripe_key()
            try:
                session = stripe_lib.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=[{
                        "price_data": {
                            "currency": currency.lower(),
                            "product_data": {"name": "Insurance Premium Payment"},
                            "unit_amount": int(amount),  # XOF is zero-decimal
                        },
                        "quantity": 1,
                    }],
                    mode="payment",
                    success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
                    cancel_url=cancel_url,
                    metadata=metadata or {},
                )
                logger.info(f"Stripe Checkout session created: {session.id}")
                return {
                    "id": session.id,
                    "url": session.url,
                    "status": "pending",
                    "gateway": "stripe",
                }
            except stripe_lib.error.StripeError as e:
                logger.error(f"Stripe checkout error: {e}")
                return {"status": "failed", "error_message": str(e), "gateway": "stripe"}
        else:
            logger.warning("Stripe not configured – simulating checkout session")
            return {
                "id": f"cs_sim_{os.urandom(8).hex()}",
                "url": f"{success_url}?session_id=cs_sim_test",
                "status": "pending",
                "gateway": "stripe",
                "simulated": True,
            }

    @staticmethod
    def verify_stripe_webhook(payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Verify and parse a Stripe webhook event."""
        if STRIPE_AVAILABLE and PaymentGatewayAPI.is_stripe_configured():
            stripe_lib.api_key = PaymentGatewayAPI._get_stripe_key()
            webhook_secret = PaymentGatewayAPI._get_stripe_webhook_secret()
            if webhook_secret:
                try:
                    event = stripe_lib.Webhook.construct_event(payload, sig_header, webhook_secret)
                    return {"valid": True, "event": event}
                except (stripe_lib.error.SignatureVerificationError, ValueError) as e:
                    logger.error(f"Stripe webhook verification failed: {e}")
                    return {"valid": False, "error": str(e)}
            else:
                # No webhook secret – parse without verification (dev only)
                return {"valid": True, "event": json.loads(payload)}
        return {"valid": False, "error": "Stripe not available"}

    # -----------------------------------------------------------------------
    # MOBILE MONEY  – Orange Money, MTN MoMo, Wave, Moov, Djamo
    # -----------------------------------------------------------------------
    @staticmethod
    def initiate_mobile_money_payment(
        amount: Decimal,
        currency: str,
        provider: str,
        phone_number: str,
        external_id: str,
        description: str = "Insurance Premium Payment",
    ) -> Dict[str, Any]:
        """Initiate a Mobile Money payment via provider API."""
        cfg = PaymentGatewayAPI._get_mobile_money_config(provider)

        if HTTPX_AVAILABLE and cfg["api_key"] and cfg["base_url"]:
            try:
                headers = {
                    "Authorization": f"Bearer {cfg['api_key']}",
                    "Content-Type": "application/json",
                    "X-Merchant-Id": cfg["merchant_id"],
                }
                payload = {
                    "amount": str(amount),
                    "currency": currency,
                    "phone_number": phone_number,
                    "external_id": external_id,
                    "description": description,
                    "callback_url": cfg["callback_url"],
                    "provider": provider,
                }

                with httpx.Client(timeout=30.0) as client:
                    response = client.post(
                        f"{cfg['base_url']}/api/v1/payments/initiate",
                        json=payload,
                        headers=headers,
                    )
                    response.raise_for_status()
                    data = response.json()

                logger.info(f"Mobile Money ({provider}) payment initiated: {data.get('transaction_id', external_id)}")
                return {
                    "status": data.get("status", "initiated"),
                    "transaction_id": data.get("transaction_id", f"{provider.upper()}-{external_id}"),
                    "provider_reference": data.get("reference", f"{provider.upper()}-{external_id}"),
                    "instructions": data.get("instructions", f"Please confirm the payment of {amount} {currency} on your phone ({phone_number})."),
                    "gateway": provider,
                }
            except Exception as e:
                logger.error(f"Mobile Money ({provider}) API error: {e}")
                return {
                    "status": "failed",
                    "error_message": str(e),
                    "gateway": provider,
                }
        else:
            # Simulation mode
            logger.warning(f"Mobile Money ({provider}) not configured – using simulation")
            return {
                "status": "initiated",
                "transaction_id": f"{provider.upper()}-{external_id}",
                "provider_reference": f"{provider.upper()}-{external_id}",
                "instructions": f"[SIMULATION] Confirm payment of {amount} {currency} on {phone_number} via {provider.replace('_money', '').capitalize()}.",
                "gateway": provider,
                "simulated": True,
            }

    @staticmethod
    def check_mobile_money_status(
        provider: str,
        transaction_id: str,
    ) -> Dict[str, Any]:
        """Check the status of a mobile money transaction."""
        cfg = PaymentGatewayAPI._get_mobile_money_config(provider)

        if HTTPX_AVAILABLE and cfg["api_key"] and cfg["base_url"]:
            try:
                headers = {
                    "Authorization": f"Bearer {cfg['api_key']}",
                    "X-Merchant-Id": cfg["merchant_id"],
                }
                with httpx.Client(timeout=15.0) as client:
                    response = client.get(
                        f"{cfg['base_url']}/api/v1/payments/{transaction_id}/status",
                        headers=headers,
                    )
                    response.raise_for_status()
                    data = response.json()
                return {
                    "status": data.get("status", "pending"),
                    "transaction_id": transaction_id,
                    "gateway": provider,
                }
            except Exception as e:
                logger.error(f"Mobile Money status check error: {e}")
                return {"status": "unknown", "error_message": str(e), "gateway": provider}
        else:
            return {"status": "completed", "transaction_id": transaction_id, "gateway": provider, "simulated": True}

    @staticmethod
    def verify_mobile_money_webhook(payload: Dict[str, Any], signature: str, provider: str) -> bool:
        """Verify mobile money webhook signature."""
        cfg = PaymentGatewayAPI._get_mobile_money_config(provider)
        if not cfg["api_secret"]:
            logger.warning(f"No API secret for {provider} – skipping webhook verification")
            return True  # Allow in dev

        expected = hmac.new(
            cfg["api_secret"].encode(),
            json.dumps(payload, sort_keys=True).encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    @staticmethod
    def verify_payment(gateway: str, payment_id: str) -> Dict[str, Any]:
        """Verify payment status from any gateway."""
        if gateway == "stripe":
            if STRIPE_AVAILABLE and PaymentGatewayAPI.is_stripe_configured():
                stripe_lib.api_key = PaymentGatewayAPI._get_stripe_key()
                try:
                    intent = stripe_lib.PaymentIntent.retrieve(payment_id)
                    return {
                        "verified": True,
                        "status": intent.status,
                        "amount": intent.amount,
                        "gateway": "stripe",
                    }
                except stripe_lib.error.StripeError as e:
                    return {"verified": False, "error": str(e), "gateway": "stripe"}
            return {"verified": True, "status": "succeeded", "gateway": "stripe", "simulated": True}
        else:
            return PaymentGatewayAPI.check_mobile_money_status(gateway, payment_id)
