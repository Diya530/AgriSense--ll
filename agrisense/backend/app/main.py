import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.api import chat, weather, crop, soil, plant_health, irrigation, market
# No auth/profile/history routers: this backend is stateless — no database,
# no server-side accounts. The farmer profile lives in the browser
# (localStorage) and is sent with requests that need it. See README for the
# architecture rationale and how to add a database back later if needed.

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("agrisense")

settings = get_settings()

app = FastAPI(
    title="AgriSense API",
    description="AI-powered smart farming advisor backend — stateless, no database required.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    if not settings.required_llm_key_present():
        logger.warning(
            "LLM_PROVIDER=%s but its API key is missing in .env. The chatbot and "
            "plant health features will return a clear 'unavailable' error until "
            "you set it. See backend/.env.example.",
            settings.LLM_PROVIDER,
        )
    else:
        logger.info("LLM provider configured: %s", settings.LLM_PROVIDER)

    if not settings.required_weather_key_present():
        logger.warning(
            "WEATHER_PROVIDER=%s but OPENWEATHERMAP_API_KEY is missing in .env. "
            "Weather features will return a clear 'unavailable' error until you "
            "set it, or switch WEATHER_PROVIDER=open-meteo (no key required).",
            settings.WEATHER_PROVIDER,
        )
    else:
        logger.info("Weather provider configured: %s", settings.WEATHER_PROVIDER)

    # RAG index is a local on-disk vector store (ChromaDB PersistentClient) —
    # a file, not a database service. Rebuilt from data/knowledge/*.md at
    # every startup so it's always in sync with the knowledge files.
    try:
        from app.rag import knowledge_base
        stats = knowledge_base.rebuild_index()
        logger.info("Knowledge base indexed: %s", stats)
    except Exception as e:
        logger.warning("Knowledge base indexing skipped/failed: %s", e)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on our end. Please try again."},
    )


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "stateless": True,
        "database_required": False,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_configured": settings.required_llm_key_present(),
        "weather_provider": settings.WEATHER_PROVIDER,
        "weather_configured": settings.required_weather_key_present(),
    }


app.include_router(chat.router)
app.include_router(weather.router)
app.include_router(crop.router)
app.include_router(soil.router)
app.include_router(plant_health.router)
app.include_router(irrigation.router)
app.include_router(market.router)
