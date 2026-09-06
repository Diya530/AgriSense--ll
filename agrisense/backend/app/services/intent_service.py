"""
Lightweight intent detection: decides whether a user message needs a live tool
call (weather) before the LLM can answer safely, to satisfy the hard rule that
weather-related answers must come from the real API, never the LLM's memory.

Keyword-based on purpose: fast, free, deterministic, easy to audit and extend —
no LLM round-trip needed just to classify intent. Runs in the target language too,
since farmers write in Hindi/Punjabi/etc.
"""
import re
from typing import Literal

Intent = Literal["weather", "irrigation", "plant_health", "general"]

WEATHER_KEYWORDS = [
    # English
    "weather", "rain", "temperature", "forecast", "humidity", "wind", "sunny",
    "cloudy", "storm", "hot", "cold", "climate today", "tomorrow",
    # Hindi (Devanagari + common romanized)
    "मौसम", "बारिश", "तापमान", "बरसात", "baarish", "barish", "mausam", "garmi", "thand",
    # Punjabi
    "ਮੌਸਮ", "ਬਾਰਿਸ਼", "mausam",
]

IRRIGATION_KEYWORDS = [
    "irrigate", "irrigation", "water the", "watering", "sinchai", "सिंचाई",
    "paani", "पानी", "ਪਾਣੀ", "spray pesticide", "spray tomorrow",
]

PLANT_HEALTH_KEYWORDS = [
    "leaves turning", "yellow leaves", "disease", "pest", "spots on leaves",
    "फसल पीली", "पत्ते", "बीमारी", "ਪੀਲੀ", "wilting", "insect",
]


def detect_intent(message: str) -> Intent:
    text = message.lower()

    if any(kw.lower() in text or kw in message for kw in WEATHER_KEYWORDS):
        return "weather"
    if any(kw.lower() in text or kw in message for kw in IRRIGATION_KEYWORDS):
        return "irrigation"
    if any(kw.lower() in text or kw in message for kw in PLANT_HEALTH_KEYWORDS):
        return "plant_health"
    return "general"


def needs_live_weather(message: str) -> bool:
    intent = detect_intent(message)
    return intent in ("weather", "irrigation") or bool(
        re.search(r"\bspray\b|\brain(y|ing)?\b|\bforecast\b", message, re.IGNORECASE)
    )
