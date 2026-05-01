"""
Multi-Provider LLM Router
Supports Google Gemini, OpenAI, and Anthropic Claude with automatic fallback.

Usage
-----
    from app.services.llm_router import LLMRouter

    router = LLMRouter(api_key=key, provider="openai")
    result = await router.generate("Summarise this policy: ...")
    print(result.text)
"""
import os
import logging
import asyncio
from typing import Optional, List, Dict, Any, AsyncIterator
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ── Optional provider imports ──────────────────────────────────────────────────

try:
    import google.generativeai as _genai
    GEMINI_AVAILABLE = True
except ImportError:
    _genai = None
    GEMINI_AVAILABLE = False

try:
    from openai import AsyncOpenAI as _AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    _AsyncOpenAI = None
    OPENAI_AVAILABLE = False

try:
    import anthropic as _anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    _anthropic = None
    ANTHROPIC_AVAILABLE = False


# ── Response dataclass ─────────────────────────────────────────────────────────

@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None and bool(self.text)


# ── Provider model defaults ────────────────────────────────────────────────────

_DEFAULT_MODELS: Dict[str, str] = {
    "gemini": "gemini-2.0-flash",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-haiku-4-5-20251001",
}

# ── Helper: detect provider from key shape ────────────────────────────────────

def _detect_provider(api_key: str) -> str:
    """Guess provider from key prefix."""
    if api_key.startswith("sk-ant-"):
        return "anthropic"
    if api_key.startswith("sk-"):
        return "openai"
    return "gemini"


# ── Main router class ──────────────────────────────────────────────────────────

class LLMRouter:
    """
    Unified async interface for Gemini, OpenAI, and Anthropic.

    Parameters
    ----------
    api_key : str
        The API key to use.
    provider : str | None
        One of 'gemini', 'openai', 'anthropic'.
        If None, auto-detected from key shape.
    model : str | None
        Override the default model for the provider.
    system_prompt : str | None
        System/context prompt prepended to every call.
    """

    def __init__(
        self,
        api_key: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        self.api_key = api_key
        self.provider = (provider or _detect_provider(api_key)).lower()
        self.model = model or _DEFAULT_MODELS.get(self.provider, "gemini-2.0-flash")
        self.system_prompt = system_prompt

    # ── Public API ─────────────────────────────────────────────────────────────

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> LLMResponse:
        """
        Generate a single response. Returns LLMResponse.
        Automatically falls back to the next available provider on failure.
        """
        providers_to_try = self._priority_list()
        last_error: Optional[str] = None

        for prov in providers_to_try:
            try:
                resp = await self._call_provider(
                    provider=prov,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    history=history or [],
                )
                if resp.success:
                    return resp
                last_error = resp.error
            except Exception as exc:
                last_error = str(exc)
                logger.warning(f"LLMRouter: {prov} failed – {exc}")

        return LLMResponse(
            text="",
            provider=self.provider,
            model=self.model,
            error=last_error or "All providers failed",
        )

    async def stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """
        Stream tokens. Falls back to non-streaming generate() if streaming not
        available for the current provider.
        """
        if self.provider == "openai" and OPENAI_AVAILABLE:
            async for chunk in self._stream_openai(prompt, temperature, max_tokens):
                yield chunk
        elif self.provider == "anthropic" and ANTHROPIC_AVAILABLE:
            async for chunk in self._stream_anthropic(prompt, temperature, max_tokens):
                yield chunk
        else:
            # Gemini streaming is blocking – wrap generate()
            resp = await self.generate(prompt, temperature, max_tokens)
            yield resp.text

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _priority_list(self) -> List[str]:
        """Return provider order: preferred first, then available fallbacks."""
        order = [self.provider]
        for p in ("gemini", "openai", "anthropic"):
            if p not in order:
                order.append(p)
        return order

    async def _call_provider(
        self,
        provider: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
        history: List[Dict[str, str]],
    ) -> LLMResponse:
        if provider == "gemini":
            return await self._call_gemini(prompt, temperature, max_tokens, history)
        if provider == "openai":
            return await self._call_openai(prompt, temperature, max_tokens, history)
        if provider == "anthropic":
            return await self._call_anthropic(prompt, temperature, max_tokens, history)
        return LLMResponse(text="", provider=provider, model="unknown", error=f"Unknown provider: {provider}")

    # ── Gemini ─────────────────────────────────────────────────────────────────

    async def _call_gemini(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        history: List[Dict[str, str]],
    ) -> LLMResponse:
        if not GEMINI_AVAILABLE:
            return LLMResponse(text="", provider="gemini", model=self.model, error="google-generativeai not installed")
        if not self.api_key:
            return LLMResponse(text="", provider="gemini", model=self.model, error="No Gemini API key")

        def _sync_call():
            _genai.configure(api_key=self.api_key)
            model_name = self.model if self.provider == "gemini" else _DEFAULT_MODELS["gemini"]
            genai_model = _genai.GenerativeModel(
                model_name,
                system_instruction=self.system_prompt,
            )
            config = _genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            # Build chat history for context
            if history:
                chat = genai_model.start_chat(history=[
                    {"role": m["role"], "parts": [m["content"]]}
                    for m in history
                    if m.get("role") in ("user", "model")
                ])
                response = chat.send_message(prompt, generation_config=config)
            else:
                response = genai_model.generate_content(prompt, generation_config=config)
            return response

        try:
            response = await asyncio.to_thread(_sync_call)
            text = response.text if hasattr(response, "text") else ""
            return LLMResponse(text=text, provider="gemini", model=self.model)
        except Exception as exc:
            return LLMResponse(text="", provider="gemini", model=self.model, error=str(exc))

    # ── OpenAI ─────────────────────────────────────────────────────────────────

    async def _call_openai(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        history: List[Dict[str, str]],
    ) -> LLMResponse:
        if not OPENAI_AVAILABLE:
            return LLMResponse(text="", provider="openai", model=self.model, error="openai not installed")
        if not self.api_key:
            return LLMResponse(text="", provider="openai", model=self.model, error="No OpenAI API key")

        model_name = self.model if self.provider == "openai" else _DEFAULT_MODELS["openai"]
        messages: List[Dict[str, str]] = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        for m in history:
            if m.get("role") in ("user", "assistant"):
                messages.append({"role": m["role"], "content": m["content"]})
        messages.append({"role": "user", "content": prompt})

        try:
            client = _AsyncOpenAI(api_key=self.api_key)
            completion = await client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            text = completion.choices[0].message.content or ""
            usage = completion.usage
            return LLMResponse(
                text=text,
                provider="openai",
                model=model_name,
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
            )
        except Exception as exc:
            return LLMResponse(text="", provider="openai", model=model_name, error=str(exc))

    # ── Anthropic ──────────────────────────────────────────────────────────────

    async def _call_anthropic(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        history: List[Dict[str, str]],
    ) -> LLMResponse:
        if not ANTHROPIC_AVAILABLE:
            return LLMResponse(text="", provider="anthropic", model=self.model, error="anthropic not installed")
        if not self.api_key:
            return LLMResponse(text="", provider="anthropic", model=self.model, error="No Anthropic API key")

        model_name = self.model if self.provider == "anthropic" else _DEFAULT_MODELS["anthropic"]
        messages: List[Dict[str, str]] = []
        for m in history:
            if m.get("role") in ("user", "assistant"):
                messages.append({"role": m["role"], "content": m["content"]})
        messages.append({"role": "user", "content": prompt})

        try:
            client = _anthropic.AsyncAnthropic(api_key=self.api_key)
            kwargs: Dict[str, Any] = {
                "model": model_name,
                "max_tokens": max_tokens,
                "messages": messages,
            }
            if self.system_prompt:
                kwargs["system"] = self.system_prompt
            response = await client.messages.create(**kwargs)
            text = response.content[0].text if response.content else ""
            return LLMResponse(
                text=text,
                provider="anthropic",
                model=model_name,
                input_tokens=response.usage.input_tokens if response.usage else 0,
                output_tokens=response.usage.output_tokens if response.usage else 0,
            )
        except Exception as exc:
            return LLMResponse(text="", provider="anthropic", model=model_name, error=str(exc))

    # ── OpenAI streaming ───────────────────────────────────────────────────────

    async def _stream_openai(
        self, prompt: str, temperature: float, max_tokens: int
    ) -> AsyncIterator[str]:
        model_name = self.model if self.provider == "openai" else _DEFAULT_MODELS["openai"]
        messages: List[Dict[str, str]] = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            client = _AsyncOpenAI(api_key=self.api_key)
            async with client.chat.completions.stream(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as exc:
            logger.error(f"OpenAI stream error: {exc}")
            yield ""

    # ── Anthropic streaming ────────────────────────────────────────────────────

    async def _stream_anthropic(
        self, prompt: str, temperature: float, max_tokens: int
    ) -> AsyncIterator[str]:
        model_name = self.model if self.provider == "anthropic" else _DEFAULT_MODELS["anthropic"]
        messages = [{"role": "user", "content": prompt}]

        try:
            client = _anthropic.AsyncAnthropic(api_key=self.api_key)
            kwargs: Dict[str, Any] = {"model": model_name, "max_tokens": max_tokens, "messages": messages}
            if self.system_prompt:
                kwargs["system"] = self.system_prompt
            async with client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as exc:
            logger.error(f"Anthropic stream error: {exc}")
            yield ""


# ── Factory: build router from AiService config ───────────────────────────────

def build_router_from_config(
    api_key: str,
    system_settings_value: Optional[Dict[str, Any]] = None,
    company_preferred_provider: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> "LLMRouter":
    """
    Construct an LLMRouter choosing the best provider based on:
    1. Company preference (from BYOK key shape / explicit setting)
    2. System admin config (provider field in AI_CONFIG)
    3. Environment variable hints
    4. Auto-detection from key shape
    """
    provider: Optional[str] = company_preferred_provider

    if not provider and system_settings_value:
        provider = system_settings_value.get("preferred_provider")

    if not provider:
        # Check env hints
        if os.getenv("OPENAI_API_KEY") and api_key == os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        elif os.getenv("ANTHROPIC_API_KEY") and api_key == os.getenv("ANTHROPIC_API_KEY"):
            provider = "anthropic"
        elif os.getenv("GOOGLE_API_KEY") and api_key == os.getenv("GOOGLE_API_KEY"):
            provider = "gemini"

    if not provider:
        provider = _detect_provider(api_key)

    return LLMRouter(api_key=api_key, provider=provider, system_prompt=system_prompt)
