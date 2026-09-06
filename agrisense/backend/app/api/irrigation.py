from fastapi import APIRouter

from app.schemas import schemas
from app.services import weather_service, geocoding_service

router = APIRouter(prefix="/api/irrigation", tags=["irrigation"])

CRITICAL_STAGES = {"flowering", "grain_filling", "tuber_bulking", "fruit_set"}


@router.post("/advise", response_model=schemas.IrrigationOut)
def advise(payload: schemas.IrrigationIn):
    profile = payload.farmer_profile

    # 1. Resolve location: explicit lat/lon > location_name > farmer_profile (client-supplied).
    lat, lon, location_used = payload.latitude, payload.longitude, None
    if lat is None or lon is None:
        if payload.location_name:
            try:
                geo = geocoding_service.geocode_location(payload.location_name)
            except geocoding_service.GeocodingError:
                geo = None
            if geo:
                lat, lon, location_used = geo["lat"], geo["lon"], geo["name"]
        if (lat is None or lon is None) and profile:
            lat, lon = profile.latitude, profile.longitude
            location_used = profile.village or profile.district
    else:
        location_used = payload.location_name or "the location you provided"

    weather_data = None
    weather_error = None
    if lat is not None and lon is not None:
        try:
            weather_data = weather_service.get_weather(lat, lon, days=3)
        except weather_service.WeatherError as e:
            weather_error = str(e)

    crop_stage = (payload.crop_stage or "").strip().lower().replace(" ", "_") or None
    is_critical_stage = crop_stage in CRITICAL_STAGES

    if payload.soil_moisture is None and weather_data is None:
        return schemas.IrrigationOut(
            decision="insufficient_data",
            reasoning="We don't have soil moisture data or a location to check the "
                      "weather forecast. Please provide soil moisture and/or set your "
                      "location in your profile, so we can give a reliable recommendation "
                      "instead of guessing.",
            location_used=location_used,
            weather_used=None,
        )

    rain_soon = False
    rain_pct = None
    steps = []

    if location_used:
        steps.append(f"Checked forecast for {location_used}.")

    if weather_data and weather_data.get("forecast"):
        next_days = weather_data["forecast"][:2]
        rain_pct = max((d.get("rain_probability_pct") or 0) for d in next_days)
        rain_soon = rain_pct >= 60
        steps.append(f"Rain probability in the next 1-2 days: {rain_pct}%.")
    elif weather_error:
        steps.append(f"Live weather forecast unavailable ({weather_error}).")

    moisture = payload.soil_moisture
    if moisture is not None:
        steps.append(f"Soil moisture reported: {moisture}%.")
    else:
        steps.append("Soil moisture not provided.")

    if payload.recent_rainfall_mm:
        steps.append(f"Recent rainfall reported: {payload.recent_rainfall_mm} mm.")

    if crop_stage:
        stage_label = crop_stage.replace("_", " ")
        steps.append(
            f"Crop stage: {stage_label}"
            + (" — a water-sensitive stage, so we lean more cautious about delaying "
               "irrigation." if is_critical_stage else ".")
        )

    if rain_soon:
        decision = "rain_sufficient"
        headline = (
            f"Rain is likely in the next 1-2 days (up to {rain_pct}% probability), "
            f"so irrigation now would likely be unnecessary and wasteful. Wait and "
            f"reassess after the rain."
        )
    elif moisture is not None and moisture < 30:
        decision = "irrigate_now"
        headline = (
            f"Soil moisture ({moisture}%) is low and no significant rain is expected "
            f"soon. Irrigation is recommended."
        )
    elif moisture is not None and moisture > 70:
        decision = "reduce"
        headline = (f"Soil moisture ({moisture}%) is already high — reduce or hold off "
                    f"irrigation to avoid waterlogging.")
    elif moisture is not None:
        decision = "wait"
        headline = f"Soil moisture ({moisture}%) is in a reasonable range. You can wait and monitor."
    elif is_critical_stage:
        decision = "irrigate_now"
        headline = (
            f"We don't have a soil moisture reading, but this is a water-sensitive growth "
            f"stage ({crop_stage.replace('_', ' ')}) and no significant rain is expected — "
            f"erring toward irrigating is safer than risking stress at this stage. A quick "
            f"manual soil check would confirm this."
        )
    else:
        decision = "insufficient_data"
        headline = ("No significant rain expected, but we don't have soil moisture "
                    "data to confirm irrigation is needed. Consider a manual soil check.")

    reasoning = headline + "\n\nHow we got here: " + " ".join(steps)
    if weather_error and weather_data is None:
        reasoning += f" (Note: live weather could not be fetched — {weather_error}. This recommendation is based on soil/crop data only.)"

    return schemas.IrrigationOut(
        decision=decision, reasoning=reasoning,
        location_used=location_used, weather_used=weather_data,
    )
