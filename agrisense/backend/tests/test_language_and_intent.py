import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.utils.language import detect_language
from app.services.intent_service import detect_intent, needs_live_weather


def test_detect_language_hindi_devanagari():
    assert detect_language("मेरी गेहूं की फसल पीली हो रही है") == "hi"


def test_detect_language_punjabi_gurmukhi():
    assert detect_language("ਮੇਰੀ ਫਸਲ ਨੂੰ ਪਾਣੀ ਕਦੋਂ ਦੇਣਾ ਚਾਹੀਦਾ ਹੈ?") == "pa"


def test_detect_language_english():
    assert detect_language("What is the weather today?") == "en"


def test_detect_language_romanized_hindi():
    assert detect_language("Kal baarish hogi kya?") == "hi"


def test_intent_weather_english():
    assert detect_intent("Will it rain tomorrow?") == "weather"


def test_intent_weather_hindi():
    assert detect_intent("कल बारिश होगी क्या?") == "weather"


def test_intent_irrigation():
    assert detect_intent("Should I irrigate my wheat today?") == "irrigation"


def test_needs_live_weather_true_for_spray_question():
    assert needs_live_weather("Should I spray pesticide tomorrow?") is True


def test_needs_live_weather_false_for_unrelated_question():
    assert needs_live_weather("What is NPK fertilizer?") is False
