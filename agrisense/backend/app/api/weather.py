from fastapi import APIRouter, HTTPException, Query

from app.schemas import schemas
from app.services import weather_service, geocoding_service

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("", response_model=schemas.WeatherResult)
def get_weather(
    latitude: float | None = Query(None),
    longitude: float | None = Query(None),
    location_name: str | None = Query(None),
    days: int = Query(7, ge=1, le=14),
):
    """Stateless: the frontend already knows the farmer's saved lat/lon (from
    localStorage) and passes it directly as latitude/longitude for "my farm"
    weather, or passes location_name to look up a different place. There's
    no server-side profile to fall back to."""
    lat, lon, resolved_name = latitude, longitude, location_name

    if (lat is None or lon is None) and location_name:
        try:
            geo = geocoding_service.geocode_location(location_name)
        except geocoding_service.GeocodingError as e:
            raise HTTPException(status_code=502, detail=str(e))
        if not geo:
            raise HTTPException(
                status_code=404,
                detail=f"Could not find a location matching '{location_name}'. "
                       f"Try a nearby city or district name.",
            )
        lat, lon, resolved_name = geo["lat"], geo["lon"], geo["name"]

    if lat is None or lon is None:
        raise HTTPException(
            status_code=400,
            detail="Provide latitude+longitude (e.g. from the saved farmer profile) "
                   "or a location_name to search.",
        )

    try:
        data = weather_service.get_weather(lat, lon, days)
    except weather_service.WeatherError as e:
        raise HTTPException(status_code=502, detail=str(e))

    data["location_name"] = data.get("location_name") or resolved_name
    return schemas.WeatherResult(**data)
