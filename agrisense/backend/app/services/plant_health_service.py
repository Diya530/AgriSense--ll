"""
Plant health analysis via a vision-capable LLM provider.

HARD RULE: if the model expresses uncertainty, gives a hedge, or the response
can't be parsed into a confident diagnosis, we set low_confidence=True and
surface that honestly rather than picking the first disease name we can find.
"""
import json
import re
from typing import Dict

from app.services.llm_provider import LLMProvider, LLMError
from app.utils.json_extract import parse_json_response

ANALYSIS_PROMPT = """You are an agricultural plant pathologist assistant analyzing a crop photo.

Look carefully at the image and respond with ONLY a single JSON object (no markdown
fences, no extra text) in exactly this shape:

{
  "crop_guess": "<likely crop name, or null if unclear>",
  "diagnosis": "<most likely disease/pest/deficiency name, or 'Healthy' if no issue is visible, or null if you cannot tell>",
  "confidence": <number 0.0-1.0, your genuine confidence in the diagnosis>,
  "symptoms": ["<visible symptom 1>", "<visible symptom 2>"],
  "recommended_action": "<concise, practical next step for the farmer>",
  "prevention": "<concise prevention tip for the future>"
}

Rules:
- If the image is blurry, too dark, not a plant, or you genuinely cannot determine
  a diagnosis, set "diagnosis" to null and "confidence" to a low number (below 0.4),
  and explain what a clearer photo would need to show in "recommended_action".
- Do not invent a specific disease name if you are not reasonably confident.
- Be conservative: for anything you are not sure about, recommend the farmer
  consult a local agricultural extension officer or plant clinic in addition to
  your suggestion.
"""

LOW_CONFIDENCE_THRESHOLD = 0.4


def analyze_plant_image(llm: LLMProvider, image_bytes: bytes, mime_type: str) -> Dict:
    try:
        raw = llm.analyze_image(image_bytes, mime_type, ANALYSIS_PROMPT)
    except LLMError:
        raise

    parsed = parse_json_response(raw)
    if parsed is None:
        # Model didn't return valid JSON — treat as low confidence rather than guessing.
        return {
            "crop_guess": None,
            "diagnosis": None,
            "confidence": 0.0,
            "symptoms": [],
            "recommended_action": "We couldn't confidently analyze this image. "
                                   "Please try a clear, well-lit, close-up photo of "
                                   "the affected leaves/plant part.",
            "prevention": None,
            "low_confidence": True,
            "note": "Analysis response could not be parsed.",
        }

    confidence = float(parsed.get("confidence") or 0.0)
    diagnosis = parsed.get("diagnosis")
    low_confidence = confidence < LOW_CONFIDENCE_THRESHOLD or not diagnosis

    return {
        "crop_guess": parsed.get("crop_guess"),
        "diagnosis": diagnosis,
        "confidence": confidence,
        "symptoms": parsed.get("symptoms") or [],
        "recommended_action": parsed.get("recommended_action"),
        "prevention": parsed.get("prevention"),
        "low_confidence": low_confidence,
        "note": ("Confidence is low — treat this as a starting point, not a definite "
                  "diagnosis. Consider consulting a local agricultural expert.")
                 if low_confidence else None,
    }

