import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services import agriculture_service


def test_recommend_crops_returns_sorted_results():
    results = agriculture_service.recommend_crops(
        n=90, p=45, k=45, temperature=25, humidity=75, rainfall=200, ph=6.2, top_k=5
    )
    assert len(results) == 5
    scores = [r["suitability_score"] for r in results]
    assert scores == sorted(scores, reverse=True)
    # Rice-friendly inputs should rank rice highly
    assert results[0]["crop"] in ("Rice", "Maize", "Sugarcane")


def test_recommend_crops_scores_bounded():
    results = agriculture_service.recommend_crops(
        n=0, p=0, k=0, temperature=50, humidity=0, rainfall=0, ph=14, top_k=12
    )
    for r in results:
        assert 0.0 <= r["suitability_score"] <= 100.0


def test_analyze_soil_flags_low_nitrogen():
    result = agriculture_service.analyze_soil(n=10, p=50, k=50, ph=6.5, moisture=50)
    assert result["nutrient_status"]["nitrogen"] == "Low"
    assert "nitrogen" in result["deficiencies"]
    assert any("Nitrogen" in g for g in result["fertilizer_guidance"])


def test_analyze_soil_ph_classification():
    acidic = agriculture_service.analyze_soil(n=80, p=50, k=50, ph=4.5, moisture=50)
    neutral = agriculture_service.analyze_soil(n=80, p=50, k=50, ph=7.0, moisture=50)
    alkaline = agriculture_service.analyze_soil(n=80, p=50, k=50, ph=9.0, moisture=50)
    assert "acidic" in acidic["ph_status"].lower()
    assert "neutral" in neutral["ph_status"].lower()
    assert "alkaline" in alkaline["ph_status"].lower()
