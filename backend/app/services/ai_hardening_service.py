"""
Tenant-safe AI production hardening helpers.

This module centralizes lightweight protections that can be reused by chat
endpoints, AI services, and specialist agents without changing their core
business logic. The service intentionally avoids persisting raw prompts: it
stores hashes, lengths, redacted previews, and tenant-scoped metadata instead.
"""
from __future__ import annotations

import asyncio
import hashlib
import inspect
import logging
import re
import uuid
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, Tuple, TypeVar

from app.core.time import utcnow

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass(frozen=True)
class PromptSafetyAssessment:
    """Result of assessing an inbound AI prompt before model execution."""

    allowed: bool
    risk_level: str
    detected_patterns: List[str] = field(default_factory=list)
    reason: Optional[str] = None
    sanitized_prompt: str = ""
    prompt_hash: str = ""
    prompt_length: int = 0

    @property
    def blocked(self) -> bool:
        return not self.allowed

    def fallback_message(self) -> str:
        if self.allowed:
            return ""
        return (
            "I cannot process requests that attempt to bypass safety rules, "
            "expose internal instructions, or reveal secrets. Please rephrase "
            "your insurance question without override instructions."
        )


@dataclass(frozen=True)
class RetryExecutionResult:
    """Metadata returned by execute_with_retries."""

    result: Any
    attempt_count: int
    fallback_used: bool
    errors: List[str] = field(default_factory=list)


class AiHardeningService:
    """
    Small production-hardening boundary for LLM calls.

    It provides three controls that are deliberately independent from any one
    model provider: prompt-safety assessment, redacted observability metadata,
    and bounded retry/fallback execution for transient model failures.
    """

    _SENSITIVE_PATTERNS: Sequence[Tuple[re.Pattern[str], str]] = (
        (re.compile(r"sk-[A-Za-z0-9_\-]{12,}"), "[REDACTED_API_KEY]"),
        (re.compile(r"ghp_[A-Za-z0-9_]{12,}"), "[REDACTED_GITHUB_TOKEN]"),
        (re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*\S+"), r"\1=[REDACTED]"),
        (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE), "[REDACTED_EMAIL]"),
        (re.compile(r"\b(?:\+?\d[\d\s().-]{7,}\d)\b"), "[REDACTED_PHONE]"),
    )

    _PROMPT_INJECTION_PATTERNS: Sequence[Tuple[re.Pattern[str], str, bool]] = (
        (
            re.compile(
                r"(?is)\b(ignore|disregard|forget|override)\b.{0,120}\b(previous|prior|above|system|developer)\b.{0,120}\b(instruction|prompt|rule|message)s?\b"
            ),
            "override_system_instructions",
            True,
        ),
        (
            re.compile(
                r"(?is)\b(reveal|show|print|dump|expose|leak|return)\b.{0,120}\b(system|developer)\b.{0,80}\b(prompt|instruction|message)s?\b"
            ),
            "system_prompt_exfiltration",
            True,
        ),
        (
            re.compile(r"(?is)\b(api[_-]?key|secret|token|password|credential)s?\b.{0,80}\b(reveal|show|print|dump|expose|leak|return)\b"),
            "secret_exfiltration",
            True,
        ),
        (
            re.compile(r"(?is)\b(jailbreak|developer mode|dan mode|disable safety|bypass guardrails)\b"),
            "jailbreak_attempt",
            True,
        ),
        (
            re.compile(r"(?is)<\s*script\b|javascript:\s*|onerror\s*="),
            "active_content_payload",
            False,
        ),
    )

    def assess_prompt(self, prompt: str, *, max_length: int = 10000) -> PromptSafetyAssessment:
        """Assess an inbound prompt and return a redacted prompt plus risk metadata."""
        original = prompt or ""
        sanitized = self.redact_text(original).strip()
        prompt_hash = hashlib.sha256(original.encode("utf-8")).hexdigest()

        detected: List[str] = []
        blocking_hits: List[str] = []
        for pattern, name, blocks in self._PROMPT_INJECTION_PATTERNS:
            if pattern.search(original):
                detected.append(name)
                if blocks:
                    blocking_hits.append(name)

        if len(original) > max_length:
            detected.append("prompt_too_long")
            blocking_hits.append("prompt_too_long")

        allowed = not blocking_hits
        if blocking_hits:
            risk_level = "blocked"
            reason = ",".join(blocking_hits)
        elif detected:
            risk_level = "elevated"
            reason = ",".join(detected)
        else:
            risk_level = "low"
            reason = None

        return PromptSafetyAssessment(
            allowed=allowed,
            risk_level=risk_level,
            detected_patterns=detected,
            reason=reason,
            sanitized_prompt=sanitized,
            prompt_hash=prompt_hash,
            prompt_length=len(original),
        )

    def redact_text(self, value: Any, *, preview_limit: int = 180) -> str:
        """Redact common secrets and PII from text before logging."""
        text = " ".join(str(value or "").split())
        for pattern, replacement in self._SENSITIVE_PATTERNS:
            text = pattern.sub(replacement, text)
        if len(text) > preview_limit:
            text = text[:preview_limit].rstrip() + "…"
        return text

    def build_observability_payload(
        self,
        *,
        company_id: Any,
        user_id: Any,
        agent_name: str,
        action: str,
        route: str,
        safety: PromptSafetyAssessment,
        history_count: int = 0,
        status: str = "started",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        attempt_count: Optional[int] = None,
        fallback_used: Optional[bool] = None,
        error: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build tenant-scoped AI call metadata without raw prompt persistence."""
        company_value = self._safe_uuid_string(company_id)
        user_value = self._safe_uuid_string(user_id)
        payload: Dict[str, Any] = {
            "trace_id": trace_id or str(uuid.uuid4()),
            "created_at": utcnow().isoformat(),
            "tenant_scope": {
                "company_id": company_value,
                "is_scoped": bool(company_value),
            },
            "user_id": user_value,
            "agent_name": agent_name,
            "action": action,
            "route": route,
            "status": status,
            "prompt": {
                "sha256": safety.prompt_hash,
                "length": safety.prompt_length,
                "redacted_preview": safety.sanitized_prompt,
            },
            "history_count": int(history_count or 0),
            "safety": {
                "allowed": safety.allowed,
                "risk_level": safety.risk_level,
                "detected_patterns": list(safety.detected_patterns),
                "reason": safety.reason,
            },
        }
        if provider:
            payload["provider"] = provider
        if model:
            payload["model"] = model
        if attempt_count is not None:
            payload["attempt_count"] = attempt_count
        if fallback_used is not None:
            payload["fallback_used"] = bool(fallback_used)
        if error:
            payload["error"] = self.redact_text(error)
        if extra:
            payload["extra"] = self._safe_extra(extra)
        return payload

    async def execute_with_retries(
        self,
        operation: Callable[[int], Awaitable[T] | T],
        *,
        max_attempts: int = 2,
        base_delay_seconds: float = 0.05,
        fallback: Optional[Callable[[BaseException, List[str]], Awaitable[T] | T]] = None,
        operation_name: str = "ai_operation",
    ) -> RetryExecutionResult:
        """Run an async/sync operation with bounded retries and optional fallback."""
        attempts = max(1, int(max_attempts or 1))
        errors: List[str] = []
        last_error: Optional[BaseException] = None

        for attempt in range(1, attempts + 1):
            try:
                result = operation(attempt)
                if inspect.isawaitable(result):
                    result = await result  # type: ignore[assignment]
                return RetryExecutionResult(
                    result=result,
                    attempt_count=attempt,
                    fallback_used=False,
                    errors=errors,
                )
            except Exception as exc:  # noqa: BLE001 - provider clients raise heterogeneous exceptions
                last_error = exc
                redacted_error = self.redact_text(exc)
                errors.append(redacted_error)
                logger.warning(
                    "AI operation failed; retrying if attempts remain",
                    extra={
                        "operation": operation_name,
                        "attempt": attempt,
                        "max_attempts": attempts,
                        "error": redacted_error,
                    },
                )
                if attempt < attempts and base_delay_seconds > 0:
                    await asyncio.sleep(base_delay_seconds * (2 ** (attempt - 1)))

        if fallback is not None and last_error is not None:
            fallback_result = fallback(last_error, errors)
            if inspect.isawaitable(fallback_result):
                fallback_result = await fallback_result  # type: ignore[assignment]
            return RetryExecutionResult(
                result=fallback_result,
                attempt_count=attempts,
                fallback_used=True,
                errors=errors,
            )

        if last_error is not None:
            raise last_error
        raise RuntimeError("AI operation failed before execution")

    def _safe_uuid_string(self, value: Any) -> Optional[str]:
        if value in (None, ""):
            return None
        try:
            return str(uuid.UUID(str(value)))
        except (TypeError, ValueError, AttributeError):
            return str(value)

    def _safe_extra(self, extra: Dict[str, Any]) -> Dict[str, Any]:
        safe: Dict[str, Any] = {}
        for key, value in extra.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                safe[str(key)] = self.redact_text(value) if isinstance(value, str) else value
            elif isinstance(value, (list, tuple)):
                safe[str(key)] = [self.redact_text(item) if isinstance(item, str) else item for item in value[:20]]
            else:
                safe[str(key)] = self.redact_text(value)
        return safe
