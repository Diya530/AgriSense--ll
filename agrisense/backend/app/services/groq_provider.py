from typing import List, Dict, Any, Optional

from app.config import get_settings
from app.services.llm_provider import LLMProvider, LLMError


class GroqProvider(LLMProvider):
    name = "groq"
    supports_vision = False
    supports_tool_calling = True

    def __init__(self):
        settings = get_settings()
        if not settings.GROQ_API_KEY:
            raise LLMError("GROQ_API_KEY is not set")
        try:
            from groq import Groq
        except ImportError as e:
            raise LLMError("groq package not installed. Run: pip install groq") from e

        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def chat(self, messages, tools: Optional[List[Dict[str, Any]]] = None,
             temperature: float = 0.4, max_tokens: int = 1024) -> Dict[str, Any]:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = (resp.choices[0].message.content or "").strip()
            if not content:
                raise LLMError("Groq returned an empty response")
            return {"content": content, "tool_calls": None}
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"Groq call failed: {e}") from e
