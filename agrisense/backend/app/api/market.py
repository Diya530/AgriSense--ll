"""
Market/mandi price route.

Live mode: if DATA_GOV_IN_API_KEY is configured, we attempt a real Agmarknet
lookup (data.gov.in) using the query as a commodity name. Note: the live
Agmarknet feed provides min/max/modal price but not MSP or trend (those
aren't part of that dataset) — live results show msp/trend as null rather
than a fabricated value.

Demo mode: if live isn't configured, or the live call fails/returns nothing,
we fall back to a small built-in sample dataset (with variety, MSP, and
trend included) and search it as free text across crop/variety/market/state
— but every response is explicitly labeled is_demo=True, so the frontend
can never present it as a live price.
"""
import os

import requests
from fastapi import APIRouter, Query

from app.schemas import schemas
from app.services.market_demo_data import search_demo_data, compute_summary, latest_update_date

router = APIRouter(prefix="/api/market", tags=["market"])

DATA_GOV_IN_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"  # Agmarknet daily prices


def _try_live(query: str):
    api_key = os.getenv("DATA_GOV_IN_API_KEY")
    if not api_key or not query.strip():
        return None
    try:
        resp = requests.get(
            f"https://api.data.gov.in/resource/{DATA_GOV_IN_RESOURCE_ID}",
            params={"api-key": api_key, "format": "json", "limit": 20,
                    "filters[commodity]": query},
            timeout=10,
        )
        resp.raise_for_status()
        records = resp.json().get("records", [])
    except requests.RequestException:
        return None

    if not records:
        return None

    return [
        schemas.MarketEntry(
            crop=r.get("commodity", query), variety=r.get("variety"),
            market=r.get("market", "Unknown"), state=r.get("state"),
            min_price=float(r.get("min_price", 0) or 0),
            max_price=float(r.get("max_price", 0) or 0),
            modal_price=float(r.get("modal_price", 0) or 0),
            msp=None, vs_msp=None, trend=None,
            date=r.get("arrival_date", ""),
        )
        for r in records
    ]


@router.get("/search", response_model=schemas.MarketSearchOut)
def search_market(q: str = Query(..., description="Free text: crop, variety, market, or state — empty returns all")):
    live_results = _try_live(q)
    if live_results:
        rows_for_summary = [r.model_dump() for r in live_results]
        return schemas.MarketSearchOut(
            query=q, is_demo=False, source="data.gov.in (Agmarknet)",
            results=live_results,
            summary=schemas.MarketSummary(**compute_summary(rows_for_summary)),
            updated=latest_update_date(rows_for_summary),
            message="Live prices don't include MSP/trend data — Agmarknet doesn't publish those fields.",
        )

    demo_rows = search_demo_data(q)
    if not demo_rows:
        return schemas.MarketSearchOut(
            query=q, is_demo=True, source="demo",
            results=[], summary=schemas.MarketSummary(rising=0, falling=0, stable=0, commodities=0),
            message=f"No demo entries match '{q}'. Try a crop name (e.g. Wheat, "
                    f"Tomato) or a market/place (e.g. Karnal, Panchkula).",
        )

    return schemas.MarketSearchOut(
        query=q, is_demo=True, source="demo",
        results=[schemas.MarketEntry(**row) for row in demo_rows],
        summary=schemas.MarketSummary(**compute_summary(demo_rows)),
        updated=latest_update_date(demo_rows),
        message="Indicative Sample Prices — Not Live. Configure DATA_GOV_IN_API_KEY "
                "in backend/.env for real mandi prices (see README > Market Data).",
    )
