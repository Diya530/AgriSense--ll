from fastapi import APIRouter

from app.schemas import schemas
from app.services import agriculture_service

router = APIRouter(prefix="/api/soil", tags=["soil"])


@router.post("/analyze", response_model=schemas.SoilAnalysisOut)
def analyze_soil(payload: schemas.SoilAnalysisIn):
    result = agriculture_service.analyze_soil(
        n=payload.nitrogen, p=payload.phosphorus, k=payload.potassium,
        ph=payload.ph, moisture=payload.moisture, soil_type=payload.soil_type,
    )
    return schemas.SoilAnalysisOut(**result)
