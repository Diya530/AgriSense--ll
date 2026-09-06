"""
LLM provider abstraction.

The rest of the app (chatbot, plant health vision, RAG answer synthesis) talks
only to `LLMProvider`. Swapping models is a one-line change in `.env`
(LLM_PROVIDER=gemini|openai|groq|ollama) with zero changes to calling code.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMError(Exception):
    """Raised when the LLM call fails after retries. Callers MUST catch this and
    return an honest 'AI assistant is temporarily unavailable' message — never
    fabricate a response in its place."""


class LLMProvider(ABC):
    name: str = "base"
    supports_vision: bool = False
    supports_tool_calling: bool = False

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.4,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        messages: [{"role": "system"|"user"|"assistant", "content": str}, ...]
        Returns: {"content": str, "tool_calls": [{"name": str, "arguments": dict}] | None}
        Raises LLMError on failure (network, auth, rate limit, empty response).
        """
        raise NotImplementedError

    def analyze_image(self, image_bytes: bytes, mime_type: str, prompt: str) -> str:
        """Vision-capable providers override this. Others raise LLMError."""
        raise LLMError(f"{self.name} does not support image analysis")


def get_llm_provider() -> LLMProvider:
    """Factory: returns the configured primary provider, wrapped with a fallback
    chain if a secondary provider is also configured (see FallbackLLMProvider)."""
    from app.config import get_settings
    settings = get_settings()

    providers_in_order = []
    primary = settings.LLM_PROVIDER

    def build(name: str) -> Optional[LLMProvider]:
        try:
            if name == "gemini" and settings.GEMINI_API_KEY:
                from app.services.gemini_provider import GeminiProvider
                return GeminiProvider()
            if name == "openai" and settings.OPENAI_API_KEY:
                from app.services.openai_provider import OpenAIProvider
                return OpenAIProvider()
            if name == "groq" and settings.GROQ_API_KEY:
                from app.services.groq_provider import GroqProvider
                return GroqProvider()
            if name == "ollama" and name == primary:
                # Only offer Ollama when it's explicitly the primary provider —
                # never silently substitute it for a misconfigured cloud
                # provider, since a "successful" build here doesn't mean a
                # local Ollama server is actually running.
                from app.services.ollama_provider import OllamaProvider
                return OllamaProvider()
        except Exception as e:
            import traceback
            print(f"Failed to build provider '{name}': {e}")
            traceback.print_exc()
            return None
        return None

    p = build(primary)
    if p:
        providers_in_order.append(p)

    # Simple fallback order: try any other configured provider before giving up.
    for name in ["gemini", "groq", "openai"]:
        if name == primary:
            continue
        alt = build(name)
        if alt:
            providers_in_order.append(alt)

    if not providers_in_order:
        raise LLMError(
            f"No LLM provider is configured. Set LLM_PROVIDER and the matching "
            f"API key in .env (see .env.example)."
        )

    return FallbackLLMProvider(providers_in_order)


class FallbackLLMProvider(LLMProvider):
    """Tries providers in order; only raises LLMError if ALL fail."""

    def __init__(self, providers: List[LLMProvider]):
        self.providers = providers
        self.name = "+".join(p.name for p in providers)
        self.supports_vision = any(p.supports_vision for p in providers)
        self.supports_tool_calling = any(p.supports_tool_calling for p in providers)

    def chat(self, messages, tools=None, temperature=0.4, max_tokens=1024):
        last_error = None
        for provider in self.providers:
            try:
                return provider.chat(messages, tools=tools, temperature=temperature,
                                      max_tokens=max_tokens)
            except LLMError as e:
                last_error = e
                continue
        raise LLMError(f"All LLM providers failed. Last error: {last_error}")

    def analyze_image(self, image_bytes, mime_type, prompt):
        last_error = None
        for provider in self.providers:
            if not provider.supports_vision:
                continue
            try:
                return provider.analyze_image(image_bytes, mime_type, prompt)
            except LLMError as e:
                last_error = e
                continue
        raise LLMError(f"No available vision-capable provider succeeded. Last error: {last_error}")
