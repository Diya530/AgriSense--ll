"""
Crop recommendation + soil analysis.

Implementation note: this uses a transparent, explainable rule/range-based
scoring model built from published agronomic requirement ranges (ICAR /
university extension guidance, condensed and summarized in our own words —
see data/knowledge/crops.md for the source ranges), NOT a black-box model
trained on synthetic data pretending to be "AI accuracy". This is intentional:
a wrong but confident ML score on fabricated training data would violate the
project's #1 rule (never invent results). The `services/` layer is structured
so a properly trained scikit-learn model (e.g. on the public "Crop
Recommendation Dataset") can be dropped in later behind the same
`recommend_crops()` function signature — see README > Known Limitations.
"""
from typing import List, Dict

# Ideal growing ranges per crop: (min, max) for each parameter.
# Sources: ICAR crop guides / agricultural university extension bulletins,
# condensed into typical Indian cultivation ranges.
CROP_REQUIREMENTS = {
    "Rice":      {"N": (60, 120), "P": (30, 60), "K": (30, 60), "temperature": (20, 35),
                  "humidity": (60, 90), "rainfall": (150, 300), "ph": (5.5, 7.0),
                  "season": ["kharif"], "water_need": "high",
                  "soil_types": ["Alluvial", "Clay", "Black (Regur)"]},
    "Wheat":     {"N": (80, 120), "P": (40, 60), "K": (30, 50), "temperature": (10, 25),
                  "humidity": (40, 70), "rainfall": (40, 100), "ph": (6.0, 7.5),
                  "season": ["rabi"], "water_need": "medium",
                  "soil_types": ["Alluvial", "Black (Regur)", "Clay"]},
    "Maize":     {"N": (80, 120), "P": (40, 60), "K": (30, 50), "temperature": (18, 32),
                  "humidity": (50, 80), "rainfall": (60, 110), "ph": (5.5, 7.5),
                  "season": ["kharif", "rabi"], "water_need": "medium",
                  "soil_types": ["Alluvial", "Red", "Black (Regur)"]},
    "Cotton":    {"N": (80, 120), "P": (30, 50), "K": (30, 60), "temperature": (21, 35),
                  "humidity": (40, 70), "rainfall": (60, 120), "ph": (6.0, 8.0),
                  "season": ["kharif"], "water_need": "medium",
                  "soil_types": ["Black (Regur)", "Alluvial"]},
    "Sugarcane": {"N": (100, 150), "P": (40, 70), "K": (60, 100), "temperature": (21, 35),
                  "humidity": (60, 85), "rainfall": (100, 200), "ph": (6.0, 7.5),
                  "season": ["kharif", "rabi", "zaid"], "water_need": "high",
                  "soil_types": ["Alluvial", "Black (Regur)", "Clay"]},
    "Mustard":   {"N": (60, 100), "P": (30, 50), "K": (20, 40), "temperature": (10, 25),
                  "humidity": (30, 60), "rainfall": (25, 60), "ph": (6.0, 7.5),
                  "season": ["rabi"], "water_need": "low",
                  "soil_types": ["Alluvial", "Sandy", "Black (Regur)"]},
    "Potato":    {"N": (100, 150), "P": (50, 80), "K": (100, 150), "temperature": (15, 25),
                  "humidity": (60, 80), "rainfall": (50, 100), "ph": (5.0, 6.5),
                  "season": ["rabi"], "water_need": "medium",
                  "soil_types": ["Alluvial", "Sandy", "Laterite"]},
    "Tomato":    {"N": (80, 120), "P": (40, 60), "K": (60, 100), "temperature": (18, 29),
                  "humidity": (50, 75), "rainfall": (40, 80), "ph": (6.0, 7.0),
                  "season": ["rabi", "zaid"], "water_need": "medium",
                  "soil_types": ["Alluvial", "Red", "Sandy"]},
    "Onion":     {"N": (60, 100), "P": (30, 50), "K": (40, 60), "temperature": (13, 28),
                  "humidity": (50, 70), "rainfall": (35, 70), "ph": (6.0, 7.0),
                  "season": ["rabi"], "water_need": "medium",
                  "soil_types": ["Alluvial", "Black (Regur)", "Red"]},
    "Chickpea":  {"N": (20, 40), "P": (40, 60), "K": (20, 40), "temperature": (10, 25),
                  "humidity": (30, 60), "rainfall": (25, 60), "ph": (6.0, 7.5),
                  "season": ["rabi"], "water_need": "low",
                  "soil_types": ["Black (Regur)", "Alluvial"]},
    "Groundnut": {"N": (20, 40), "P": (40, 60), "K": (40, 60), "temperature": (22, 32),
                  "humidity": (50, 75), "rainfall": (50, 120), "ph": (6.0, 7.0),
                  "season": ["kharif"], "water_need": "low",
                  "soil_types": ["Sandy", "Red", "Laterite"]},
    "Soybean":   {"N": (20, 40), "P": (40, 60), "K": (30, 50), "temperature": (20, 32),
                  "humidity": (55, 80), "rainfall": (60, 120), "ph": (6.0, 7.5),
                  "season": ["kharif"], "water_need": "medium",
                  "soil_types": ["Black (Regur)", "Red"]},
}

WATER_AVAILABILITY_RANK = {"low": 0, "medium": 1, "high": 2}
WATER_NEED_RANK = {"low": 0, "medium": 1, "high": 2}


def _range_score(value: float, low: float, high: float) -> float:
    """1.0 if inside range; decays smoothly to 0 the further outside it is."""
    if low <= value <= high:
        return 1.0
    span = max(high - low, 1e-6)
    dist = (low - value) if value < low else (value - high)
    return max(0.0, 1.0 - dist / span)


def recommend_crops(n: float, p: float, k: float, temperature: float, humidity: float,
                     rainfall: float, ph: float, top_k: int = 5) -> List[Dict]:
    inputs = {"N": n, "P": p, "K": k, "temperature": temperature,
              "humidity": humidity, "rainfall": rainfall, "ph": ph}
    results = []
    for crop, ranges in CROP_REQUIREMENTS.items():
        scores = {param: _range_score(inputs[param], *ranges[param]) for param in inputs}
        overall = sum(scores.values()) / len(scores)
        weak_points = [p for p, s in scores.items() if s < 0.5]
        if overall >= 0.75:
            explanation = f"{crop} matches your soil and climate conditions well."
        elif weak_points:
            explanation = (f"{crop} is a partial match — {', '.join(weak_points)} "
                            f"is/are outside the typical ideal range.")
        else:
            explanation = f"{crop} is a moderate match for your conditions."
        results.append({
            "crop": crop,
            "suitability_score": round(overall * 100, 1),
            "explanation": explanation,
        })
    results.sort(key=lambda r: r["suitability_score"], reverse=True)
    return results[:top_k]


def recommend_crops_basic(season: str = None, soil_type: str = None,
                           water_availability: str = None, current_crop: str = None,
                           farming_goal: str = None, top_k: int = 5) -> List[Dict]:
    """Farmer-friendly recommendation path: no NPK/pH required. Scores crops by
    how well they match season, soil type, and water availability — the
    information most farmers actually know offhand. Deprioritizes the
    farmer's current crop slightly to nudge toward rotation, since repeating
    the same crop season after season is a common soil-health pitfall."""
    season = (season or "").strip().lower() or None
    soil_type = (soil_type or "").strip() or None
    water_availability = (water_availability or "").strip().lower() or None

    results = []
    for crop, meta in CROP_REQUIREMENTS.items():
        score = 0.0
        max_score = 0.0
        reasons = []

        if season:
            max_score += 1
            if season in meta["season"]:
                score += 1
            else:
                reasons.append(f"typically grown in {'/'.join(meta['season'])} season, not {season}")

        if soil_type:
            max_score += 1
            if soil_type in meta["soil_types"]:
                score += 1
            else:
                reasons.append(f"prefers {', '.join(meta['soil_types'])} soil")

        if water_availability and water_availability in WATER_AVAILABILITY_RANK:
            max_score += 1
            avail_rank = WATER_AVAILABILITY_RANK[water_availability]
            need_rank = WATER_NEED_RANK[meta["water_need"]]
            if need_rank <= avail_rank:
                score += 1
            else:
                reasons.append(f"needs {meta['water_need']} water availability")

        # If the farmer gave us nothing to score against, treat everything as
        # a loose/equal match rather than silently returning zero for all.
        suitability = (score / max_score * 100) if max_score > 0 else 60.0

        # Gentle rotation nudge: same crop as current season after season is
        # a common soil-health issue — don't exclude it, just don't lead with it.
        if current_crop and current_crop.strip().lower() == crop.lower():
            suitability = max(0.0, suitability - 15)
            reasons.append("you're already growing this — consider rotating for soil health")

        if reasons:
            explanation = f"{crop}: " + "; ".join(reasons) + "."
        else:
            explanation = f"{crop} is a good match for the conditions you described."

        results.append({
            "crop": crop,
            "suitability_score": round(suitability, 1),
            "explanation": explanation,
        })

    results.sort(key=lambda r: r["suitability_score"], reverse=True)
    return results[:top_k]


# General guidance by soil type, used when lab values (NPK/pH/moisture)
# aren't available — keeps the Soil Analysis page useful without a lab test.
SOIL_TYPE_GENERIC_GUIDANCE = {
    "Alluvial": "Alluvial soil is generally fertile and well-suited to a wide "
                "range of crops (wheat, rice, sugarcane, most vegetables). It "
                "usually holds nutrients and moisture reasonably well.",
    "Black (Regur)": "Black soil retains moisture well and is well-suited to "
                      "cotton, soybean, and pulses, but can become waterlogged "
                      "if drainage is poor.",
    "Red": "Red soil is often lower in nitrogen and phosphorus naturally and "
           "drains quickly — groundnut, millets, and pulses tend to do well; "
           "organic matter/compost helps water retention.",
    "Laterite": "Laterite soil is often acidic and low in natural fertility — "
                "crops like groundnut and cashew tend to tolerate it better; "
                "liming can help if it's strongly acidic.",
    "Sandy": "Sandy soil drains quickly and doesn't hold nutrients or water "
             "well — more frequent, lighter irrigation and organic matter "
             "additions generally help; groundnut and root vegetables often "
             "do reasonably well.",
    "Clay": "Clay soil holds water and nutrients well but can drain poorly "
            "and compact easily — rice and wheat often do well, but watch "
            "for waterlogging after heavy rain.",
}


def analyze_soil(n: float = None, p: float = None, k: float = None, ph: float = None,
                  moisture: float = None, soil_type: str = None) -> Dict:
    have_any_lab_value = any(v is not None for v in (n, p, k, ph, moisture))

    # pH status — only if provided
    if ph is None:
        ph_status = "Not provided — a soil test would tell you this precisely."
    elif ph < 5.5:
        ph_status = "Strongly acidic"
    elif ph < 6.5:
        ph_status = "Slightly acidic"
    elif ph <= 7.5:
        ph_status = "Neutral (ideal for most crops)"
    elif ph <= 8.5:
        ph_status = "Slightly alkaline"
    else:
        ph_status = "Strongly alkaline"

    def nutrient_level(value, low, high):
        if value is None:
            return "Unknown"
        if value < low:
            return "Low"
        if value > high:
            return "High"
        return "Adequate"

    nutrient_status = {
        "nitrogen": nutrient_level(n, 40, 100),
        "phosphorus": nutrient_level(p, 20, 60),
        "potassium": nutrient_level(k, 20, 60),
        "moisture": nutrient_level(moisture, 30, 70),
    }

    deficiencies = [k_ for k_, v in nutrient_status.items() if v == "Low"]

    fertilizer_guidance = []
    if nutrient_status["nitrogen"] == "Low":
        fertilizer_guidance.append(
            "Nitrogen is low — consider urea or a nitrogen-rich fertilizer in split doses.")
    if nutrient_status["phosphorus"] == "Low":
        fertilizer_guidance.append(
            "Phosphorus is low — DAP or single super phosphate (SSP) can help at sowing.")
    if nutrient_status["potassium"] == "Low":
        fertilizer_guidance.append(
            "Potassium is low — muriate of potash (MOP) is commonly used to correct this.")
    if not fertilizer_guidance and have_any_lab_value:
        fertilizer_guidance.append(
            "N, P, and K you provided are within adequate ranges — maintain with routine "
            "balanced fertilization.")
    elif not fertilizer_guidance:
        fertilizer_guidance.append(
            "No lab values provided, so we can't say whether fertilizer is needed — "
            "a soil test (often free/low-cost through your state agricultural department) "
            "will give you a precise answer.")

    improvement_recommendations = []
    if ph_status in ("Strongly acidic", "Slightly acidic"):
        improvement_recommendations.append(
            "Consider agricultural lime to raise soil pH gradually; retest after a season.")
    if ph_status in ("Strongly alkaline", "Slightly alkaline"):
        improvement_recommendations.append(
            "Consider gypsum or organic matter to help lower soil pH over time.")
    if nutrient_status["moisture"] == "Low":
        improvement_recommendations.append(
            "Moisture is low — check irrigation scheduling and consider mulching to retain water.")
    if nutrient_status["moisture"] == "High":
        improvement_recommendations.append(
            "Moisture is high — ensure adequate drainage to avoid root/fungal issues.")

    used_generic_guidance = False
    if soil_type and soil_type in SOIL_TYPE_GENERIC_GUIDANCE:
        improvement_recommendations.append(SOIL_TYPE_GENERIC_GUIDANCE[soil_type])
        used_generic_guidance = not have_any_lab_value

    if not improvement_recommendations:
        improvement_recommendations.append(
            "Soil conditions look reasonably balanced based on what you provided.")

    if have_any_lab_value:
        suitable = recommend_crops(
            n if n is not None else 80, p if p is not None else 45,
            k if k is not None else 45, temperature=25, humidity=60, rainfall=80,
            ph=ph if ph is not None else 6.5, top_k=5,
        )
        suitable_crops = [c["crop"] for c in suitable if c["suitability_score"] >= 50] \
            or [c["crop"] for c in suitable[:3]]
    elif soil_type:
        suitable_crops = [
            crop for crop, meta in CROP_REQUIREMENTS.items()
            if soil_type in meta["soil_types"]
        ][:5]
    else:
        suitable_crops = []

    return {
        "ph_status": ph_status,
        "nutrient_status": nutrient_status,
        "deficiencies": deficiencies,
        "suitable_crops": suitable_crops,
        "fertilizer_guidance": fertilizer_guidance,
        "improvement_recommendations": improvement_recommendations,
        "used_generic_guidance": used_generic_guidance,
    }
