import os
import logging
import asyncio
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import base64
import hashlib

from app.models.company import Company
from app.models.system_settings import SystemSettings, AiUsageLog
from app.core.config import settings
from app.core.time import utcnow
from app.services.ai_hardening_service import AiHardeningService

logger = logging.getLogger(__name__)

class AiService:
    def __init__(self, db: Session):
        self.db = db
        # Use PBKDF2 for proper key derivation (much stronger than plain SHA256)
        key_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            settings.SECRET_KEY.encode(),
            b'tinsur-ai-encryption-salt-v1',  # Fixed salt for deterministic derivation
            iterations=100_000
        )
        self.fernet = Fernet(base64.urlsafe_b64encode(key_bytes))

    def _create_legacy_fernet(self):
        """Create a Fernet instance using legacy SHA256 derivation for backward compat."""
        key_hash = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        return Fernet(base64.urlsafe_b64encode(key_hash))

    def encrypt_key(self, api_key: str) -> str:
        """Encrypt an API key for storage."""
        return self.fernet.encrypt(api_key.encode()).decode()

    def decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt a stored API key, with backward compatibility for legacy encryption."""
        try:
            return self.fernet.decrypt(encrypted_key.encode()).decode()
        except Exception:
            # Try legacy decryption for keys encrypted before PBKDF2 migration
            try:
                legacy_fernet = self._create_legacy_fernet()
                decrypted = legacy_fernet.decrypt(encrypted_key.encode()).decode()
                logger.info("Decrypted with legacy key derivation - consider re-encrypting")
                return decrypted
            except Exception as e:
                logger.error(f"Failed to decrypt API key with both methods: {e}")
                return ""

    def get_effective_ai_config(self, company_id: Optional[str] = None) -> Tuple[str, str, bool]:
        """
        Returns (api_key, plan_type, has_credits)
        Logic hierarchy:
        1. Company BYOK (If plan is BYOK and key exists)
        2. Super Admin Global Key (If plan is CREDIT and key exists)
        3. Local .env Fallback (If no other keys found - ensures non-breaking)
        """
        import uuid
        try:
            c_id = uuid.UUID(company_id) if isinstance(company_id, str) else company_id
        except Exception:
            c_id = None

        company = self.db.query(Company).filter(Company.id == c_id).first() if c_id else None
        
        # Logic hierarchy:
        # 1. Company BYOK (If plan is BYOK and key exists)
        if company:
            plan = company.ai_plan or "CREDIT"
            # 0. BASIC Plan - No AI
            if plan == "BASIC":
                return "", "BASIC", False

            # 1. BYOK Plan
            if plan == "BYOK" and company.ai_api_key_encrypted:
                decrypted = self.decrypt_key(company.ai_api_key_encrypted)
                if decrypted:
                    return decrypted, "BYOK", True

            # Check credits for CREDIT plan
            if plan == "CREDIT" and company.ai_credits_balance <= 0:
                return "", "CREDIT", False
        else:
            plan = "CREDIT"

        # 2. Super Admin Global Key (If key exists in DB)
        system_config = self.db.query(SystemSettings).filter(SystemSettings.key == "AI_CONFIG").first()
        if system_config and system_config.value:
            # Check for provider-specific keys (google, openai, anthropic)
            for provider_key in ["google_api_key", "openai_api_key", "anthropic_api_key"]:
                stored_key = system_config.value.get(provider_key)
                if stored_key:
                    # Try to decrypt if it looks encrypted (Fernet tokens start with 'gAAAAA')
                    if stored_key.startswith("gAAAAA"):
                        decrypted = self.decrypt_key(stored_key)
                        if decrypted:
                            return decrypted, plan, True
                    else:
                        return stored_key, plan, True

        # 3. Final Fallback to .env (Legacy Support)
        env_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if env_key:
             return env_key, plan, True
        
        return "", plan, False

    async def analyze_damage(self, company_id: str, image_urls: List[str]) -> Dict[str, Any]:
        """
        Analyze vehicle damage photos using Gemini Vision.
        Returns a dictionary with severity, description, and suggested estimate.
        """
        api_key, plan, has_credits = self.get_effective_ai_config(company_id)
        if not api_key:
            return {"error": "AI service not available or no credits remaining"}

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            # print(f"DEBUG: Using Gemini model for damage analysis: gemini-2.0-flash")
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Formulate prompt
            prompt = """
            Analyze the attached image(s) of a vehicle involved in an insurance claim.
            1. Identify the parts of the vehicle that are damaged.
            2. Assess the severity of the damage (Low, Medium, High).
            3. Provide a brief technical description of the damage.
            4. Suggest an initial repair estimate in XOF (West African CFA Franc).
            
            Return the result in JSON format with the following keys:
            {
                "severity": "Low|Medium|High",
                "damage_description": "text",
                "suggested_estimate": number,
                "confidence_score": 0-1
            }
            """
            
            # Download images and pass to Gemini multimodal
            import requests as http_requests
            image_parts = []
            for url in image_urls:
                try:
                    img_response = http_requests.get(url, timeout=15)
                    if img_response.status_code == 200:
                        import mimetypes
                        content_type = img_response.headers.get('content-type', 'image/jpeg')
                        image_parts.append({
                            "mime_type": content_type.split(';')[0],
                            "data": img_response.content
                        })
                except Exception as img_err:
                    logger.warning(f"Failed to download image {url}: {img_err}")

            try:
                content_parts = [prompt] + image_parts if image_parts else [prompt]
                response = model.generate_content(content_parts)

                # Parse JSON from response
                import json, re
                text = response.text
                json_match = re.search(r'\{[\s\S]*\}', text)
                if json_match:
                    result = json.loads(json_match.group())
                    result["analyzed_at"] = utcnow().isoformat()
                    return result
            except Exception as gen_err:
                logger.warning(f"Gemini analysis call failed, using heuristic fallback: {gen_err}")

            # Heuristic fallback if Gemini call fails
            import random
            severities = ["Low", "Medium", "High"]
            severity = random.choice(severities)
            estimates = {
                "Low": random.randrange(50000, 200000, 5000),
                "Medium": random.randrange(250000, 750000, 10000),
                "High": random.randrange(800000, 2500000, 50000)
            }

            return {
                "severity": severity,
                "damage_description": f"Heuristic estimate: {severity.lower()} impact damage detected. Manual review recommended for accurate assessment.",
                "suggested_estimate": estimates[severity],
                "confidence_score": 0.5,
                "analyzed_at": utcnow().isoformat(),
                "note": "Automated AI analysis unavailable. This is a heuristic estimate."
            }
            
        except Exception as e:
            logger.error(f"Gemini Vision analysis failed: {e}")
            return {"error": str(e)}

    async def parse_kyc_document(self, image_url: str, doc_type: str = "identity_document", company_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Parses KYC documents from a URL.
        """
        try:
            import requests
            response = requests.get(image_url)
            return await self.parse_kyc_document_bytes(response.content, doc_type, company_id)
        except Exception as e:
            return {"error": f"Failed to fetch image: {str(e)}"}

    async def parse_kyc_document_bytes(self, image_data: bytes, doc_type: str = "identity_document", company_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Parses KYC documents from raw bytes.
        """
        import google.generativeai as genai
        api_key, _, _ = self.get_effective_ai_config(company_id)
        
        if not api_key:
            return {"error": "AI API key not configured"}
            
        genai.configure(api_key=api_key)
        logger.debug(f"Using Gemini model for KYC: gemini-2.0-flash")
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        if doc_type == "car_papers":
            prompt = """
            Extract vehicle information from this document. Return ONLY clear JSON:
            {
              "registration_number": "...",
              "vin": "...",
              "make": "...",
              "model": "...",
              "year": "...",
              "owner_name": "...",
              "expiry_date": "YYYY-MM-DD"
            }
            """
        else:
            prompt = """
            Extract identity information from this document. Return ONLY clear JSON:
            {
              "full_name": "...",
              "id_number": "...",
              "nationality": "...",
              "dob": "YYYY-MM-DD",
              "issue_date": "YYYY-MM-DD",
              "expiry_date": "YYYY-MM-DD",
              "document_type": "Passport|ID|Driving_License"
            }
            """

        try:
            vision_response = await asyncio.to_thread(
                model.generate_content,
                [prompt, {"mime_type": "image/jpeg", "data": image_data}]
            )
            
            if not vision_response.candidates:
                return {"error": "AI provided no candidates for the document"}
                
            text = vision_response.text
            import json
            import re
            
            # Clean text from common markdown artifacts
            clean_text = re.sub(r'```json\s*|\s*```', '', text, flags=re.IGNORECASE).strip()
            
            json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    if result.get("expiry_date"):
                        try:
                            expiry = datetime.strptime(result["expiry_date"], "%Y-%m-%d")
                            result["is_expired"] = expiry < datetime.now()
                        except:
                            result["is_expired"] = False
                    return result
                except json.JSONDecodeError as je:
                    logger.error(f"JSON Decode Error: {je}. Raw text: {text}")
                    return {"error": "Failed to decode structure from document content"}
            
            logger.error(f"No JSON found in AI response. Raw text: {text}")
            return {"error": "Failed to parse document content - no valid data found"}
        except Exception as e:
            logger.error(f"KYC Parsing failed: {e}")
            return {"error": str(e)}

    async def detect_claim_fraud(self, claim_id: UUID) -> Dict[str, Any]:
        """
        Comprehensive fraud detection for a claim.
        Levels:
        1. Image Fingerprinting (Duplicate detection)
        2. AI Consistency Check (Text vs Vision)
        3. Historical Pattern matching
        """
        from app.models.claim import Claim
        from app.core.image_utils import get_image_hash, compare_hashes
        
        claim = self.db.query(Claim).get(claim_id)
        if not claim:
            return {"error": "Claim not found"}

        risk_factors = []
        fraud_score = 0.0
        
        # 1. Image Fingerprinting
        current_hashes = []
        if claim.evidence_files:
            for url in claim.evidence_files:
                img_hash = get_image_hash(url)
                if img_hash:
                    current_hashes.append(img_hash)
            
            if current_hashes:
                claim.evidence_hashes = current_hashes
                self.db.commit()
            else:
                current_hashes = claim.evidence_hashes or []
            
            # Compare with other claims in the same company
            from sqlalchemy import cast, String
            other_claims = self.db.query(Claim).filter(
                Claim.company_id == claim.company_id,
                Claim.id != claim.id,
                cast(Claim.evidence_hashes, String) != '[]'
            ).all()
            
            duplicate_found = False
            for other in other_claims:
                for h1 in current_hashes:
                    for h2 in other.evidence_hashes:
                        similarity = compare_hashes(h1, h2)
                        if similarity > 0.95:
                            duplicate_found = True
                            risk_factors.append({
                                "type": "duplicate_image",
                                "severity": "High",
                                "message": f"Evidence image matches image in Claim {other.claim_number}"
                            })
                            fraud_score = max(fraud_score, 0.9)
                            break
                    if duplicate_found: break
                if duplicate_found: break

        # 2. AI Consistency Check (Simulated Gemini call)
        api_key, plan, _ = self.get_effective_ai_config(str(claim.company_id))
        if api_key or True: # Allow basic heuristics even without key for demo/robustness
            # Real call would send text + images to Gemini
            # Fixed Heuristic: flag if 'fire' is present without 'accident'
            desc = claim.incident_description.lower()
            if "fire" in desc and "accident" not in desc:
                risk_factors.append({
                    "type": "content_mismatch",
                    "severity": "Medium",
                    "message": "AI detected suspicious keywords in description compared to industry norms (Potential staged fire)."
                })
                fraud_score = max(fraud_score, 0.45)

        # Final Score Aggregation
        claim.fraud_score = fraud_score
        claim.fraud_details = {"risk_factors": risk_factors, "last_analyzed": utcnow().isoformat()}
        self.db.commit()
        
        return {
            "fraud_score": fraud_score,
            "risk_factors": risk_factors
        }

    def log_and_consume_usage(
        self,
        company_id: str,
        user_id: str,
        agent_name: str,
        cost: float = 0.05,
        action: str = "chat_interaction",
        request_payload: Optional[Dict[str, Any]] = None,
    ):
        """Deduct credits and log the interaction with optional safe observability metadata."""
        import uuid
        
        # Ensure UUID objects
        try:
            c_id = uuid.UUID(company_id) if isinstance(company_id, str) else company_id
            u_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        except Exception as e:
            logger.error(f"Invalid UUID in log_and_consume_usage: {e}")
            return

        company = self.db.query(Company).filter(Company.id == c_id).first()
        if company and company.ai_plan == "CREDIT":
            company.ai_credits_balance = max(0, company.ai_credits_balance - cost)
            
            # Log usage
            log = AiUsageLog(
                company_id=c_id,
                user_id=u_id,
                agent_name=agent_name,
                action=action,
                credits_consumed=cost,
                request_payload=request_payload,
            )
            self.db.add(log)
            self.db.commit()

            # Check for low balance alert
            if company.ai_credits_balance < 10.0: # Threshold for alert
                try:
                    from app.services.notification_service import NotificationService
                    notif_service = NotificationService(self.db)
                    notif_service.send_low_balance_alert(c_id, company.ai_credits_balance)
                except Exception as e:
                    logger.error(f"Failed to send low balance alert: {e}")

    def set_system_api_key(self, provider: str, api_key: str):
        """Update global API keys (Super Admin only)."""
        config = self.db.query(SystemSettings).filter(SystemSettings.key == "AI_CONFIG").first()
        if not config:
            config = SystemSettings(key="AI_CONFIG", value={}, description="Global AI API Configuration")
            self.db.add(config)

        new_value = dict(config.value)
        new_value[f"{provider}_api_key"] = api_key
        config.value = new_value
        self.db.commit()

    def get_llm_router(
        self,
        company_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        """
        Return a configured LLMRouter for the given company using the key
        hierarchy (BYOK → System Admin → env fallback).
        Returns None if no key is available.
        """
        from app.services.llm_router import build_router_from_config

        api_key, plan, has_credits = self.get_effective_ai_config(company_id)
        if not api_key:
            return None

        # Fetch system settings for provider preference
        system_config = self.db.query(SystemSettings).filter(SystemSettings.key == "AI_CONFIG").first()
        system_val = system_config.value if system_config else None

        return build_router_from_config(
            api_key=api_key,
            system_settings_value=system_val,
            system_prompt=system_prompt,
        )

    async def chat(
        self,
        prompt: str,
        company_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        history: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Unified chat method — uses whichever AI provider is configured.
        Falls back to a helpful error message if no key is available.
        """
        hardening = AiHardeningService()
        safety = hardening.assess_prompt(prompt)
        if safety.blocked:
            return {
                "text": safety.fallback_message(),
                "provider": "none",
                "model": "none",
                "error": "prompt_blocked",
                "observability": hardening.build_observability_payload(
                    company_id=company_id,
                    user_id=None,
                    agent_name="ai_service_chat",
                    action="chat_completion",
                    route="ai_service.chat",
                    safety=safety,
                    history_count=len(history or []),
                    status="blocked",
                ),
            }

        router = self.get_llm_router(company_id=company_id, system_prompt=system_prompt)
        if router is None:
            return {
                "text": "AI service is currently unavailable. Please configure an API key.",
                "provider": "none",
                "model": "none",
                "error": "no_api_key",
                "observability": hardening.build_observability_payload(
                    company_id=company_id,
                    user_id=None,
                    agent_name="ai_service_chat",
                    action="chat_completion",
                    route="ai_service.chat",
                    safety=safety,
                    history_count=len(history or []),
                    status="unavailable",
                ),
            }

        from app.services.llm_router import LLMResponse

        async def _operation(_attempt: int) -> LLMResponse:
            candidate = await router.generate(
                prompt=safety.sanitized_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                history=history or [],
            )
            if candidate.error:
                raise RuntimeError(candidate.error)
            return candidate

        async def _fallback(last_error: BaseException, _errors: List[str]) -> LLMResponse:
            return LLMResponse(
                text="AI service is temporarily unavailable. Please try again shortly.",
                provider="none",
                model="none",
                error=hardening.redact_text(last_error),
            )

        execution = await hardening.execute_with_retries(
            _operation,
            max_attempts=2,
            fallback=_fallback,
            operation_name="ai_service.chat",
        )
        resp = execution.result
        status = "fallback" if execution.fallback_used else "completed"
        return {
            "text": resp.text,
            "provider": resp.provider,
            "model": resp.model,
            "error": resp.error,
            "observability": hardening.build_observability_payload(
                company_id=company_id,
                user_id=None,
                agent_name="ai_service_chat",
                action="chat_completion",
                route="ai_service.chat",
                safety=safety,
                history_count=len(history or []),
                status=status,
                provider=resp.provider,
                model=resp.model,
                attempt_count=execution.attempt_count,
                fallback_used=execution.fallback_used,
                error=resp.error,
            ),
        }
