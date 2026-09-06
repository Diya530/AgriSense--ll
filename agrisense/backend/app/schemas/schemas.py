from typing import Optional, List, Any, Literal

from pydantic import BaseModel, Field


# ---------- Farmer profile context ----------
# The farmer profile lives in the browser (localStorage), not on the server.
# This shape is sent by the frontend as part of any request that benefits
# from personalization (chat, irrigation). Every field is optional — the app
# must work fine with an empty/partial profile.
class FarmerProfileContext(BaseModel):
    name: Optional[str] = None
    preferred_language: Optional[str] = "en"
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    land_area_acres: Optional[float] = None
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    current_crop: Optional[str] = None
    farming_goals: Optional[str] = None


# ---------- Weather ----------
class WeatherResult(BaseModel):
    source: str
    is_cached: bool = False
    fetched_at: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    current: Optional[dict] = None
    forecast: Optional[list] = None
    stale_warning: Optional[str] = None
    error: Optional[str] = None


# ---------- Chat ----------
class ChatHistoryTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatMessageIn(BaseModel):
    message: str
    language: Optional[str] = None  # if None, auto-detected
    # Conversation memory lives in the browser tab's state, not the server —
    # the frontend sends recent turns with each request. Capped server-side
    # to keep token usage sane (see memory_service.py).
    history: Optional[List[ChatHistoryTurn]] = None
    farmer_profile: Optional[FarmerProfileContext] = None


class ChatMessageOut(BaseModel):
    reply: str
    language: str
    tool_calls: Optional[List[dict]] = None
    sources: Optional[List[dict]] = None


# ---------- Crop recommendation ----------
class CropRecommendationIn(BaseModel):
    crop_interest: Optional[str] = None
    location: Optional[str] = None
    season: Optional[str] = None
    soil_type: Optional[str] = None
    water_availability: Optional[str] = None
    land_area_acres: Optional[float] = None
    farming_goal: Optional[str] = None
    current_or_previous_crop: Optional[str] = None

    has_soil_test: bool = False
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rainfall: Optional[float] = None
    ph: Optional[float] = None


class CropSuggestion(BaseModel):
    crop: str
    suitability_score: float
    explanation: str


class CropRecommendationOut(BaseModel):
    results: List[CropSuggestion]
    model_used: str


# ---------- Soil analysis ----------
class SoilAnalysisIn(BaseModel):
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    ph: Optional[float] = None
    moisture: Optional[float] = None
    soil_type: Optional[str] = None


class SoilAnalysisOut(BaseModel):
    ph_status: str
    nutrient_status: dict
    deficiencies: List[str]
    suitable_crops: List[str]
    fertilizer_guidance: List[str]
    improvement_recommendations: List[str]
    used_generic_guidance: bool = False


# ---------- Irrigation ----------
class IrrigationIn(BaseModel):
    crop: Optional[str] = None
    soil_moisture: Optional[float] = None
    crop_stage: Optional[str] = None
    recent_rainfall_mm: Optional[float] = None
    irrigation_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    farmer_profile: Optional[FarmerProfileContext] = None


class IrrigationOut(BaseModel):
    decision: Literal["irrigate_now", "wait", "reduce", "rain_sufficient", "insufficient_data"]
    reasoning: str
    location_used: Optional[str] = None
    weather_used: Optional[dict] = None


# ---------- Plant health ----------
class PlantHealthOut(BaseModel):
    crop_guess: Optional[str]
    diagnosis: Optional[str]
    confidence: Optional[float]
    symptoms: Optional[List[str]]
    recommended_action: Optional[str]
    prevention: Optional[str]
    low_confidence: bool
    note: Optional[str] = None


# ---------- Market ----------
class MarketEntry(BaseModel):
    crop: str
    variety: Optional[str] = None
    market: str
    state: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    modal_price: float
    msp: Optional[float] = None
    vs_msp: Optional[float] = None
    trend: Optional[str] = None
    unit: str = "per quintal"
    date: str


class MarketSummary(BaseModel):
    rising: int
    falling: int
    stable: int
    commodities: int


class MarketSearchOut(BaseModel):
    query: str
    is_demo: bool
    source: str
    results: List[MarketEntry]
    summary: MarketSummary
    updated: Optional[str] = None
    message: Optional[str] = None
