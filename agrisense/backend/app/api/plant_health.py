from fastapi import APIRouter, HTTPException, UploadFile, File

from app.config import get_settings
from app.schemas import schemas
from app.services.llm_provider import get_llm_provider, LLMError
from app.services.plant_health_service import analyze_plant_image

router = APIRouter(prefix="/api/plant-health", tags=["plant-health"])
settings = get_settings()


@router.post("/analyze", response_model=schemas.PlantHealthOut)
async def analyze(image: UploadFile = File(...)):
    allowed_types = settings.ALLOWED_IMAGE_TYPES.split(",")
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type '{image.content_type}'. Allowed: {allowed_types}",
        )

    contents = await image.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_MB:
        raise HTTPException(
            status_code=400,
            detail=f"Image too large ({size_mb:.1f}MB). Max allowed: {settings.MAX_UPLOAD_MB}MB.",
        )
    if size_mb == 0:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.")

    llm = get_llm_provider()
    if not llm.supports_vision:
        raise HTTPException(
            status_code=503,
            detail="No vision-capable AI provider is configured. Set LLM_PROVIDER=gemini "
                   "or openai (both support image analysis) in .env.",
        )

    try:
        result = analyze_plant_image(llm, contents, image.content_type)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"We could not analyze this image: {e}")

    return schemas.PlantHealthOut(**result)
