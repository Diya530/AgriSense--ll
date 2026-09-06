"""Shared helper for parsing JSON out of an LLM's text response, tolerating
markdown code fences or minor wrapping text. Used by any vision-analysis
service (plant health, soil report extraction) that asks the model to
respond with strict JSON."""
import json
import re
from typing import Optional


def parse_json_response(raw: str) -> Optional[dict]:
    raw = raw.strip()
    raw = re.sub(r"^```(json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
        return None
