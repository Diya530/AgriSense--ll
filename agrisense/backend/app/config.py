"""
Central configuration. Loads from environment variables (.env) via pydantic-settings.
This backend is intentionally stateless: no database, no server-side accounts.
The farmer profile lives in the browser (localStorage) and is sent to the
backend as part of each request that needs it (chat, irrigation, etc).
"""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    APP_NAME: str = "AgriSense"
    ENV: str = "development"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # --- LLM Provider ---
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.6-flash"
    GEMINI_VISION_MODEL: str = "gemini-3.6-flash"

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"

    # --- Weather ---
    WEATHER_PROVIDER: str = "openweathermap"
    OPENWEATHERMAP_API_KEY: Optional[str] = None
    WEATHER_CACHE_TTL_MINUTES: int = 30  # in-memory cache, resets on restart

    # --- Geocoding ---
    GEOCODING_PROVIDER: str = "openweathermap"

    # --- RAG (file-based, no database — just a local vector index on disk) ---
    KNOWLEDGE_DIR: str = "../data/knowledge"
    VECTOR_DB_DIR: str = "./vector_store"

    # --- Uploads ---
    MAX_UPLOAD_MB: int = 8
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp"

    def required_llm_key_present(self) -> bool:
        mapping = {
            "gemini": self.GEMINI_API_KEY,
            "openai": self.OPENAI_API_KEY,
            "groq": self.GROQ_API_KEY,
            "ollama": "local",
        }
        return bool(mapping.get(self.LLM_PROVIDER))

    def required_weather_key_present(self) -> bool:
        if self.WEATHER_PROVIDER == "open-meteo":
            return True
        return bool(self.OPENWEATHERMAP_API_KEY)


@lru_cache
def get_settings() -> Settings:
    return Settings()
