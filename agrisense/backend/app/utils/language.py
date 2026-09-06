"""
Lightweight language detection.

Strategy:
1. Script-based detection first (fast, free, very reliable for Indic scripts —
   Devanagari for Hindi/Marathi, Gurmukhi for Punjabi, Bengali script, etc.)
2. Fall back to `langdetect` for Latin-script text (English vs. romanized Hindi/
   Punjabi is genuinely ambiguous — we bias toward English unless there are strong
   romanized-Hindi/Punjabi cues, then let the LLM's own language judgement take over
   in the system prompt, since it's more reliable than any lightweight heuristic here).
"""
import re

# Unicode block ranges for supported Indian scripts
SCRIPT_RANGES = {
    "hi": ("\u0900", "\u097F"),  # Devanagari (Hindi, Marathi share this — see below)
    "pa": ("\u0A00", "\u0A7F"),  # Gurmukhi (Punjabi)
    "bn": ("\u0980", "\u09FF"),  # Bengali
    "te": ("\u0C00", "\u0C7F"),  # Telugu
    "ta": ("\u0B80", "\u0BFF"),  # Tamil
    "gu": ("\u0A80", "\u0AFF"),  # Gujarati
    "kn": ("\u0C80", "\u0CFF"),  # Kannada
    "ml": ("\u0D00", "\u0D7F"),  # Malayalam
    "or": ("\u0B00", "\u0B7F"),  # Odia
}

# Common Marathi-only markers to disambiguate from Hindi within Devanagari script
MARATHI_HINTS = ["आहे", "मी", "तुम्ही", "काय", "करतो", "आणि"]

LANGUAGE_NAMES = {
    "en": "English", "hi": "Hindi", "pa": "Punjabi", "bn": "Bengali",
    "mr": "Marathi", "te": "Telugu", "ta": "Tamil", "gu": "Gujarati",
    "kn": "Kannada", "ml": "Malayalam", "or": "Odia",
}

ROMANIZED_HINDI_PUNJABI_WORDS = {
    "kya", "kab", "kaise", "kaisa", "kyu", "kyun", "mera", "meri", "mere",
    "hai", "hoga", "hogi", "karna", "kheth", "khet", "fasal", "paani",
    "baarish", "barish", "sinchai", "kal", "aaj",
    "tuhada", "tuhadi", "ki", "menu", "assi", "sadi",  # Punjabi-ish romanized
}


def detect_language(text: str) -> str:
    """Return an ISO-ish code: en, hi, pa, bn, mr, te, ta, gu, kn, ml, or."""
    if not text or not text.strip():
        return "en"

    for code, (start, end) in SCRIPT_RANGES.items():
        if any(start <= ch <= end for ch in text):
            if code == "hi" and any(hint in text for hint in MARATHI_HINTS):
                return "mr"
            return code

    # Latin script: check for romanized Hindi/Punjabi farmer phrasing
    lowered = re.findall(r"[a-zA-Z]+", text.lower())
    hits = sum(1 for w in lowered if w in ROMANIZED_HINDI_PUNJABI_WORDS)
    if hits >= 1 and hits / max(len(lowered), 1) > 0.15:
        return "hi"  # treat romanized Hindi/Punjabi as Hindi by default; LLM adapts

    try:
        from langdetect import detect
        code = detect(text)
        return code if code in LANGUAGE_NAMES else "en"
    except Exception:
        return "en"


def language_name(code: str) -> str:
    return LANGUAGE_NAMES.get(code, "English")
