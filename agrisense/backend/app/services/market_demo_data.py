"""
Demo/sample market price dataset — loaded from a static JSON file
(data/market/demo_prices.json), not a database. Used ONLY when a live
data.gov.in key is not configured or the live call fails, and always
clearly labeled as demo data by the API and the UI.
"""
import json
import os

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                           "data", "market", "demo_prices.json")

_cache = None


def _load() -> list:
    global _cache
    if _cache is None:
        with open(os.path.abspath(_DATA_PATH), "r", encoding="utf-8") as f:
            _cache = json.load(f)
    return _cache


def _vs_msp(row):
    if row.get("msp") is None:
        return None
    return row["modal_price"] - row["msp"]


def _with_derived_fields(row):
    return {**row, "unit": "per quintal", "vs_msp": _vs_msp(row)}


def search_demo_data(query: str):
    """Free-text search across crop, variety, market, and state fields
    (case-insensitive, substring match, all terms must match somewhere)."""
    rows = _load()
    if query and query.strip():
        terms = query.lower().split()
        rows = [
            row for row in rows
            if all(term in f"{row['crop']} {row['variety']} {row['market']} {row['state']}".lower()
                   for term in terms)
        ]
    return [_with_derived_fields(r) for r in rows]


def compute_summary(rows):
    rising = sum(1 for r in rows if r.get("trend") == "up")
    falling = sum(1 for r in rows if r.get("trend") == "down")
    stable = sum(1 for r in rows if r.get("trend") == "stable")
    commodities = len({r["crop"] for r in rows})
    return {"rising": rising, "falling": falling, "stable": stable, "commodities": commodities}


def latest_update_date(rows):
    dates = [r["date"] for r in rows if r.get("date")]
    return max(dates) if dates else None
