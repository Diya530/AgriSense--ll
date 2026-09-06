import base64
from typing import List, Dict, Any, Optional

from app.config import get_settings
from app.services.llm_provider import LLMProvider, LLMError


class OpenAIProvider(LLMProvider):
    name = "openai"
    supports_vision = True
    supports_tool_calling = True

    def __init__(self):
        settings = get_settings()
        if not settings.OPENAI_API_KEY:
            raise LLMError("OPENAI_API_KEY is not set")
        try:
            from openai import OpenAI
        except ImportError as e:
            raise LLMError("openai package not installed. Run: pip install openai") from e

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

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
                raise LLMError("OpenAI returned an empty response")
            return {"content": content, "tool_calls": None}
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"OpenAI call failed: {e}") from e

    def analyze_image(self, image_bytes: bytes, mime_type: str, prompt: str) -> str:
        try:
            b64 = base64.b64encode(image_bytes).decode("utf-8")
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url",
                         "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
                    ],
                }],
                max_tokens=800,
                temperature=0.2,
            )
            content = (resp.choices[0].message.content or "").strip()
            if not content:
                raise LLMError("OpenAI vision returned an empty response")
            return content
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"OpenAI vision call failed: {e}") from e
