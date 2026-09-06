import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services import agriculture_service
from app.services.market_demo_data import search_demo_data


def test_recommend_crops_basic_no_inputs_still_returns_results():
    results = agriculture_service.recommend_crops_basic()
    assert len(results) == 5
    for r in results:
        assert 0 <= r["suitability_score"] <= 100


def test_recommend_crops_basic_matches_season_and_soil():
    results = agriculture_service.recommend_crops_basic(
        season="rabi", soil_type="Alluvial", water_availability="medium"
    )
    top_crops = [r["crop"] for r in results[:3]]
    # Wheat is a rabi crop suited to alluvial soil with medium water — should rank well.
    assert "Wheat" in top_crops


def test_recommend_crops_basic_deprioritizes_current_crop():
    with_repeat = agriculture_service.recommend_crops_basic(
        season="rabi", soil_type="Alluvial", current_crop="Wheat"
    )
    wheat_score = next(r["suitability_score"] for r in with_repeat if r["crop"] == "Wheat")
    without_repeat = agriculture_service.recommend_crops_basic(
        season="rabi", soil_type="Alluvial"
    )
    wheat_score_no_repeat = next(r["suitability_score"] for r in without_repeat if r["crop"] == "Wheat")
    assert wheat_score < wheat_score_no_repeat


def test_analyze_soil_handles_all_missing_values():
    result = agriculture_service.analyze_soil(soil_type="Sandy")
    assert result["used_generic_guidance"] is True
    assert result["ph_status"].startswith("Not provided")
    assert len(result["suitable_crops"]) > 0


def test_market_demo_search_by_crop():
    results = search_demo_data("wheat")
    assert len(results) > 0
    assert all("wheat" in r["crop"].lower() for r in results)


def test_market_demo_search_by_place():
    results = search_demo_data("panchkula")
    assert len(results) > 0
    assert all("panchkula" in r["market"].lower() for r in results)


def test_market_demo_search_combined():
    results = search_demo_data("panchkula wheat")
    assert len(results) > 0
    for r in results:
        assert "panchkula" in r["market"].lower()
        assert "wheat" in r["crop"].lower()


def test_market_demo_search_no_match():
    results = search_demo_data("nonexistent crop xyz")
    assert results == []
