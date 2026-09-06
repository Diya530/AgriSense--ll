"""
Geocoding: turn "Chandigarh" / "Sonipat, Haryana" / a PIN code into lat/lon.
Uses OpenWeatherMap's Geocoding API if a key is present (same key as weather),
otherwise falls back to Open-Meteo's free geocoding endpoint (no key required).
"""
from typing import Optional

import requests

from app.config import get_settings


class GeocodingError(Exception):
    pass


def geocode_location(query: str) -> Optional[dict]:
    """Returns {"name": str, "state": str|None, "country": str, "lat": float, "lon": float}
    or None if no match was found. Raises GeocodingError only on transport failure."""
    settings = get_settings()
    query = query.strip()
    if not query:
        return None

    if settings.OPENWEATHERMAP_API_KEY:
        try:
            resp = requests.get(
                "https://api.openweathermap.org/geo/1.0/direct",
                params={"q": query, "limit": 1, "appid": settings.OPENWEATHERMAP_API_KEY},
                timeout=10,
            )
            resp.raise_for_status()
            results = resp.json()
            if results:
                r = results[0]
                return {
                    "name": r.get("name"), "state": r.get("state"),
                    "country": r.get("country"),
                    "lat": r["lat"], "lon": r["lon"],
                }
        except requests.RequestException as e:
            raise GeocodingError(f"Geocoding request failed: {e}") from e

    # Fallback: Open-Meteo geocoding (free, no key)
    try:
        resp = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": query, "count": 1, "language": "en"},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("results")
        if results:
            r = results[0]
            return {
                "name": r.get("name"), "state": r.get("admin1"),
                "country": r.get("country_code"),
                "lat": r["latitude"], "lon": r["longitude"],
            }
    except requests.RequestException as e:
        raise GeocodingError(f"Geocoding request failed: {e}") from e

    return None
