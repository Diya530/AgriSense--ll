"""
Weather service.

HARD RULE: this module either returns real data from a live API (or a clearly
labeled cached copy of real data), or raises WeatherError. It must never
invent values.

Stateless-backend note: caching is an in-process, in-memory dict rather than
a database table. This means the cache resets on every backend restart —
that's an acceptable trade-off for avoiding a database dependency, and the
cache's only job is to survive brief upstream API hiccups within a single
run, not to persist across deploys.
"""
import datetime as dt
from typing import Optional

import requests

from app.config import get_settings

# module-level in-memory cache: {"lat,lon": {"payload": dict, "fetched_at": datetime}}
_WEATHER_CACHE: dict = {}


class WeatherError(Exception):
    pass


def _cache_key(lat: float, lon: float) -> str:
    return f"{round(lat, 2)},{round(lon, 2)}"


def _get_cached(lat: float, lon: float) -> Optional[dict]:
    entry = _WEATHER_CACHE.get(_cache_key(lat, lon))
    if not entry:
        return None
    settings = get_settings()
    age = dt.datetime.utcnow() - entry["fetched_at"]
    payload = dict(entry["payload"])
    payload["is_cached"] = age > dt.timedelta(minutes=settings.WEATHER_CACHE_TTL_MINUTES)
    payload["fetched_at"] = entry["fetched_at"].isoformat()
    return payload


def _store_cache(lat: float, lon: float, payload: dict):
    _WEATHER_CACHE[_cache_key(lat, lon)] = {
        "payload": payload, "fetched_at": dt.datetime.utcnow(),
    }


def _fetch_openweathermap(lat: float, lon: float, days: int) -> dict:
    settings = get_settings()
    if not settings.OPENWEATHERMAP_API_KEY:
        raise WeatherError(
            "OPENWEATHERMAP_API_KEY is not configured. Add it to backend/.env "
            "(get a free key at https://openweathermap.org/api)."
        )
    key = settings.OPENWEATHERMAP_API_KEY

    try:
        current_resp = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat": lat, "lon": lon, "appid": key, "units": "metric"},
            timeout=10,
        )
        current_resp.raise_for_status()
        current = current_resp.json()

        forecast_resp = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={"lat": lat, "lon": lon, "appid": key, "units": "metric"},
            timeout=10,
        )
        forecast_resp.raise_for_status()
        forecast_raw = forecast_resp.json()
    except requests.Timeout as e:
        raise WeatherError("Weather service timed out. Please try again.") from e
    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        if status == 401:
            raise WeatherError("Weather API key is invalid or not yet activated.") from e
        raise WeatherError(f"Weather service returned an error (HTTP {status}).") from e
    except requests.RequestException as e:
        raise WeatherError(f"Could not reach weather service: {e}") from e

    daily = {}
    for entry in forecast_raw.get("list", []):
        date_str = entry["dt_txt"].split(" ")[0]
        d = daily.setdefault(date_str, {
            "date": date_str, "temps": [], "pop": [], "conditions": [], "wind": [],
        })
        d["temps"].append(entry["main"]["temp"])
        d["pop"].append(entry.get("pop", 0.0))
        d["conditions"].append(entry["weather"][0]["main"])
        d["wind"].append(entry["wind"]["speed"])

    forecast_days = []
    for date_str, d in list(daily.items())[:days]:
        forecast_days.append({
            "date": date_str,
            "temp_min": round(min(d["temps"]), 1),
            "temp_max": round(max(d["temps"]), 1),
            "rain_probability_pct": round(max(d["pop"]) * 100),
            "condition": max(set(d["conditions"]), key=d["conditions"].count),
            "wind_speed_ms": round(sum(d["wind"]) / len(d["wind"]), 1),
        })

    return {
        "source": "openweathermap",
        "location_name": current.get("name") or f"{lat},{lon}",
        "latitude": lat,
        "longitude": lon,
        "current": {
            "temperature_c": current["main"]["temp"],
            "feels_like_c": current["main"]["feels_like"],
            "humidity_pct": current["main"]["humidity"],
            "condition": current["weather"][0]["main"],
            "description": current["weather"][0]["description"],
            "wind_speed_ms": current["wind"]["speed"],
            "sunrise": dt.datetime.utcfromtimestamp(
                current["sys"]["sunrise"]).isoformat() + "Z",
            "sunset": dt.datetime.utcfromtimestamp(
                current["sys"]["sunset"]).isoformat() + "Z",
        },
        "forecast": forecast_days,
    }


def _fetch_open_meteo(lat: float, lon: float, days: int) -> dict:
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat, "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,"
                         "weather_code,wind_speed_10m_max",
                "timezone": "auto",
                "forecast_days": min(days, 16),
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise WeatherError(f"Could not reach weather service: {e}") from e

    cur = data.get("current", {})
    daily = data.get("daily", {})
    forecast_days = []
    for i, date_str in enumerate(daily.get("time", [])[:days]):
        forecast_days.append({
            "date": date_str,
            "temp_min": daily["temperature_2m_min"][i],
            "temp_max": daily["temperature_2m_max"][i],
            "rain_probability_pct": daily.get("precipitation_probability_max", [None] * (i + 1))[i],
            "condition": _wmo_code_to_text(daily["weather_code"][i]),
            "wind_speed_ms": round(daily["wind_speed_10m_max"][i] / 3.6, 1),
        })

    return {
        "source": "open-meteo",
        "location_name": f"{lat},{lon}",
        "latitude": lat,
        "longitude": lon,
        "current": {
            "temperature_c": cur.get("temperature_2m"),
            "feels_like_c": cur.get("temperature_2m"),
            "humidity_pct": cur.get("relative_humidity_2m"),
            "condition": _wmo_code_to_text(cur.get("weather_code")),
            "description": _wmo_code_to_text(cur.get("weather_code")),
            "wind_speed_ms": round((cur.get("wind_speed_10m") or 0) / 3.6, 1),
            "sunrise": None,
            "sunset": None,
        },
        "forecast": forecast_days,
    }


def _wmo_code_to_text(code: Optional[int]) -> str:
    mapping = {
        0: "Clear", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Fog", 51: "Light drizzle", 61: "Light rain",
        63: "Moderate rain", 65: "Heavy rain", 71: "Snow", 80: "Rain showers",
        95: "Thunderstorm",
    }
    return mapping.get(code, "Unknown") if code is not None else "Unknown"


def get_weather(lat: float, lon: float, days: int = 7) -> dict:
    """Main entry point. Tries the configured provider, falls back to the
    in-memory cache on failure, and raises WeatherError only if BOTH live
    fetch and cache fail."""
    settings = get_settings()
    provider = settings.WEATHER_PROVIDER

    try:
        if provider == "open-meteo":
            payload = _fetch_open_meteo(lat, lon, days)
        else:
            payload = _fetch_openweathermap(lat, lon, days)
        payload["is_cached"] = False
        payload["fetched_at"] = dt.datetime.utcnow().isoformat()
        _store_cache(lat, lon, payload)
        return payload
    except WeatherError as e:
        cached = _get_cached(lat, lon)
        if cached:
            cached["stale_warning"] = str(e)
            return cached
        raise
