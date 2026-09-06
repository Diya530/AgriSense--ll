from typing import List, Dict, Any, Optional

import requests

from app.config import get_settings
from app.services.llm_provider import LLMProvider, LLMError


class OllamaProvider(LLMProvider):
    name = "ollama"
    supports_vision = False
    supports_tool_calling = False

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL

    def chat(self, messages, tools: Optional[List[Dict[str, Any]]] = None,
             temperature: float = 0.4, max_tokens: int = 1024) -> Dict[str, Any]:
        try:
            resp = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": temperature, "num_predict": max_tokens},
                },
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            content = (data.get("message", {}).get("content") or "").strip()
            if not content:
                raise LLMError("Ollama returned an empty response")
            return {"content": content, "tool_calls": None}
        except LLMError:
            raise
        except requests.RequestException as e:
            raise LLMError(
                f"Could not reach local Ollama server at {self.base_url}. "
                f"Is `ollama serve` running? ({e})"
            ) from e
        except Exception as e:
            raise LLMError(f"Ollama call failed: {e}") from e
