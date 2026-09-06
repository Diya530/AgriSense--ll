from fastapi import APIRouter

from app.schemas import schemas
from app.services import agriculture_service

router = APIRouter(prefix="/api/crop", tags=["crop"])


@router.post("/recommend", response_model=schemas.CropRecommendationOut)
def recommend_crop(payload: schemas.CropRecommendationIn):
    advanced_fields_present = payload.has_soil_test and all(
        v is not None for v in (payload.nitrogen, payload.phosphorus, payload.potassium,
                                 payload.temperature, payload.humidity, payload.rainfall, payload.ph)
    )

    if advanced_fields_present:
        results = agriculture_service.recommend_crops(
            n=payload.nitrogen, p=payload.phosphorus, k=payload.potassium,
            temperature=payload.temperature, humidity=payload.humidity,
            rainfall=payload.rainfall, ph=payload.ph,
        )
        model_used = "range-based agronomic scoring using your soil-test values"
    else:
        results = agriculture_service.recommend_crops_basic(
            season=payload.season, soil_type=payload.soil_type,
            water_availability=payload.water_availability,
            current_crop=payload.current_or_previous_crop,
            farming_goal=payload.farming_goal,
        )
        model_used = ("farmer-friendly scoring using season/soil type/water availability "
                      "(add soil-test values for a more precise NPK-based estimate)")

    return schemas.CropRecommendationOut(
        results=[schemas.CropSuggestion(**r) for r in results],
        model_used=model_used,
    )
