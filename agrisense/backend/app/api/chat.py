import re
import logging

from fastapi import APIRouter, HTTPException

from app.schemas import schemas
from app.services import weather_service, geocoding_service, intent_service, memory_service
from app.services.llm_provider import get_llm_provider, LLMError
from app.rag import knowledge_base
from app.utils.language import detect_language, language_name

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger("agrisense")

SYSTEM_PROMPT_TEMPLATE = """You are AgriSense, an AI farming advisor for Indian farmers.

RESPOND IN: {language_name} (the farmer wrote to you in {language_name}). Keep it
natural and simple — a farmer with limited technical background should understand
you easily. If the farmer mixes languages, respond naturally, matching their style.

HARD RULES (never break these):
- Never invent weather data, sensor readings, prices, or API results. If live data
  was retrieved below, use it. If it says unavailable, say so honestly — do not
  guess a plausible-sounding number instead.
- Weather is forecast information, not certainty. Never phrase a rain probability
  as a guarantee (e.g. never say "0% means it definitely won't rain" or "it will
  rain"). Instead say things like "According to the current forecast, the chance
  of rain is X%." Always attribute weather claims to the forecast, not to fact.
- Forecasts are based on the nearest weather grid point, not an on-farm sensor.
  If the farmer asks about hyper-local/on-farm conditions specifically, briefly
  clarify that this is the nearest available forecast point, not an exact
  reading from their field.
- Always be clear about WHICH location a weather answer is for — the farmer's
  saved farm location or an explicitly named place — using the phrasing given
  in the weather tool result below. Never blend or confuse the two.
- Never claim you analyzed an image unless image analysis results are given to you.
- Never fabricate studies, sources, or statistics. If you're not sure, say so.
- For agricultural advice that depends on exact soil test values, local variety,
  or season, mention that dependency rather than giving a falsely confident answer.
- For high-risk decisions (large pesticide applications, major input costs), lean
  conservative and suggest confirming with a local agricultural extension officer.
- Keep answers reasonably concise and structured (short sections/bullets), not
  walls of text, unless the farmer clearly wants deep detail.
- Do not use markdown formatting like **bold**, *italics*, or # headers — this
  chat interface displays plain text only, so markdown symbols would show up
  as literal asterisks/hashes instead of formatting. Use plain sentences and
  simple dashes for lists instead.

FARMER PROFILE:
{profile_context}

{weather_context}

{rag_context}
"""


def _strip_markdown(text: str) -> str:
    """Safety net: strip common markdown symbols in case the model uses them
    despite the system prompt instruction not to. Bullet markers ("* item")
    are converted to plain dashes BEFORE italic-stripping runs — otherwise a
    bullet's "*" incorrectly pairs with a later "*" and everything between
    them gets deleted, truncating the reply."""
    text = re.sub(r"^[ \t]*[\*\+]\s+", "- ", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^\n*]+?)\*(?!\*)", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    return text


def _resolve_location_for_message(message: str, profile: schemas.FarmerProfileContext | None):
    """Location priority: explicit place named in this message > saved profile
    location. Returns (lat, lon, display_name, is_explicit, error)."""
    match = re.search(r"(?:in|at|near|for)\s+([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)*)", message)
    candidate = match.group(1).strip() if match else None

    if not candidate:
        match2 = re.search(
            r"([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)*)\s+(?:weather|mausam|ka\s+mausam|ki\s+mausam)",
            message,
        )
        candidate = match2.group(1).strip() if match2 else None

    if candidate:
        try:
            geo = geocoding_service.geocode_location(candidate)
        except geocoding_service.GeocodingError:
            geo = None
        if geo:
            return geo["lat"], geo["lon"], geo["name"], True, None

    if profile and profile.latitude and profile.longitude:
        return profile.latitude, profile.longitude, (profile.village or profile.district), False, None

    return None, None, None, False, "no_location"


def _profile_context(profile: schemas.FarmerProfileContext | None) -> str:
    if not profile:
        return "No profile information available yet."
    parts = []
    if profile.current_crop:
        parts.append(f"Current crop: {profile.current_crop}")
    if profile.soil_type:
        parts.append(f"Soil type: {profile.soil_type}")
    if profile.land_area_acres:
        parts.append(f"Land area: {profile.land_area_acres} acres")
    if profile.irrigation_type:
        parts.append(f"Irrigation type: {profile.irrigation_type}")
    if profile.village or profile.district or profile.state:
        loc = ", ".join(filter(None, [profile.village, profile.district, profile.state]))
        parts.append(f"Location: {loc}")
    if profile.farming_goals:
        parts.append(f"Farming goals: {profile.farming_goals}")
    return "; ".join(parts) if parts else "No profile details filled in yet."


@router.post("", response_model=schemas.ChatMessageOut)
def send_message(payload: schemas.ChatMessageIn):
    profile = payload.farmer_profile

    # 1. Language: explicit request > detected script in this message >
    # farmer's saved profile language > English.
    detected = detect_language(payload.message)
    if payload.language:
        lang_code = payload.language
    elif detected != "en":
        lang_code = detected
    elif profile and profile.preferred_language and profile.preferred_language != "en":
        lang_code = profile.preferred_language
    else:
        lang_code = detected
    lang_name = language_name(lang_code)

    tool_calls_log = []
    sources_log = []
    weather_context = ""

    # 2. Weather tool call, if the intent requires it
    if intent_service.needs_live_weather(payload.message):
        lat, lon, loc_name, is_explicit, err = _resolve_location_for_message(payload.message, profile)
        if err == "no_location":
            weather_context = (
                "WEATHER TOOL: could not be called — no location is known. "
                "Ask the farmer which village/city/district to check, or tell them "
                "to set their location in their profile."
            )
        else:
            try:
                data = weather_service.get_weather(lat, lon, days=7)
                tool_calls_log.append({"tool": "weather", "location": loc_name,
                                        "lat": lat, "lon": lon, "explicit": is_explicit})
                cached_note = " (NOTE: this is cached data, may be stale)" if data.get(
                    "is_cached") else ""
                location_label = (
                    f"the EXPLICITLY REQUESTED location '{loc_name}' (not the farmer's saved "
                    f"farm location — this request named a different place, so use '{loc_name}' "
                    f"in your reply, e.g. 'Weather for {loc_name}...')"
                    if is_explicit else
                    f"the FARMER'S SAVED FARM LOCATION '{loc_name}' (say something like "
                    f"'Weather for your farm in {loc_name}...')"
                )
                weather_context = (
                    f"WEATHER TOOL RESULT for {location_label}{cached_note} "
                    f"(source: {data['source']}):\n"
                    f"Current: {data['current']}\n"
                    f"7-day forecast: {data['forecast']}\n"
                    f"Use ONLY these numbers for any weather-related claim in your answer. "
                    f"Clearly state which location this forecast is for, using the phrasing above."
                )
                sources_log.append({"type": "weather_api", "provider": data["source"],
                                     "location": loc_name, "explicit": is_explicit})
            except weather_service.WeatherError as e:
                weather_context = (
                    f"WEATHER TOOL RESULT: FAILED ({e}). Tell the farmer honestly that "
                    f"live weather is temporarily unavailable — do NOT invent a forecast."
                )

    # 3. RAG retrieval
    rag_chunks = knowledge_base.retrieve(payload.message, top_k=4)
    if rag_chunks:
        rag_text = "\n\n".join(f"[{c['source']}]: {c['text']}" for c in rag_chunks)
        rag_context = (f"RELEVANT KNOWLEDGE BASE EXCERPTS (cite the source name if you "
                        f"use these):\n{rag_text}")
        sources_log.extend([{"type": "knowledge_base", "source": c["source"]} for c in rag_chunks])
    else:
        rag_context = "No specific knowledge base match found for this query — use general reasoning."

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        language_name=lang_name,
        profile_context=_profile_context(profile),
        weather_context=weather_context,
        rag_context=rag_context,
    )

    # 4. Build message history (client-supplied) + this new user turn
    llm = get_llm_provider()
    history = [{"role": t.role, "content": t.content} for t in (payload.history or [])]
    context_messages = memory_service.build_context_messages(history, llm)
    messages = ([{"role": "system", "content": system_prompt}] + context_messages
                + [{"role": "user", "content": payload.message}])

    # 5. Call the LLM
    try:
        result = llm.chat(messages, temperature=0.4, max_tokens=900)
        reply_text = _strip_markdown(result["content"])
    except LLMError as e:
        logger.error(f"LLM chat call failed: {e}")
        reply_text = (
            "AI assistant is temporarily unavailable right now. Please try again "
            "in a moment."
            if lang_code == "en" else
            "AI सहायक अभी अस्थायी रूप से उपलब्ध नहीं है। कृपया थोड़ी देर बाद फिर से प्रयास करें।"
        )

    return schemas.ChatMessageOut(
        reply=reply_text,
        language=lang_code,
        tool_calls=tool_calls_log or None,
        sources=sources_log or None,
    )
