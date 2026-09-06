import json
from typing import List, Dict, Any, Optional

from app.config import get_settings
from app.services.llm_provider import LLMProvider, LLMError


class GeminiProvider(LLMProvider):
    name = "gemini"
    supports_vision = True
    supports_tool_calling = True

    def __init__(self):
        settings = get_settings()
        if not settings.GEMINI_API_KEY:
            raise LLMError("GEMINI_API_KEY is not set")
        try:
            import google.generativeai as genai
        except ImportError as e:
            raise LLMError(
                "google-generativeai package not installed. Run: pip install google-generativeai"
            ) from e

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._genai = genai
        self.model_name = settings.GEMINI_MODEL
        self.vision_model_name = settings.GEMINI_VISION_MODEL

    @staticmethod
    def _to_gemini_history(messages: List[Dict[str, str]]):
        """Gemini wants a system_instruction plus a user/model-alternating history."""
        system_parts = []
        history = []
        for m in messages:
            if m["role"] == "system":
                system_parts.append(m["content"])
            elif m["role"] == "user":
                history.append({"role": "user", "parts": [m["content"]]})
            elif m["role"] == "assistant":
                history.append({"role": "model", "parts": [m["content"]]})
        return "\n\n".join(system_parts), history

    def chat(self, messages, tools: Optional[List[Dict[str, Any]]] = None,
             temperature: float = 0.4, max_tokens: int = 1024) -> Dict[str, Any]:
        system_instruction, history = self._to_gemini_history(messages)
        try:
            model = self._genai.GenerativeModel(
                self.model_name,
                system_instruction=system_instruction or None,
            )
            # Function/tool calling: Gemini supports native tool declarations, but to
            # keep this abstraction provider-agnostic and simple, we use a
            # JSON-instruction convention (see rag/intent handling) rather than
            # binding native tool schemas here. This keeps behavior identical
            # across providers that don't support native tool calling (e.g. Ollama).
            convo = model.start_chat(history=history[:-1] if history else [])
            last_user = history[-1]["parts"][0] if history else ""
            response = convo.send_message(
                last_user,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            text = (response.text or "").strip()
            if not text:
                raise LLMError("Gemini returned an empty response")
            return {"content": text, "tool_calls": None}
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"Gemini call failed: {e}") from e

    def analyze_image(self, image_bytes: bytes, mime_type: str, prompt: str) -> str:
        try:
            model = self._genai.GenerativeModel(self.vision_model_name)
            response = model.generate_content(
                [prompt, {"mime_type": mime_type, "data": image_bytes}],
                generation_config={"temperature": 0.2, "max_output_tokens": 800},
            )
            text = (response.text or "").strip()
            if not text:
                raise LLMError("Gemini vision returned an empty response")
            return text
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"Gemini vision call failed: {e}") from e
