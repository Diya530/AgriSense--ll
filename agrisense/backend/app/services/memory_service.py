"""
Conversation memory — stateless version.

The frontend keeps the full conversation in React state (per browser tab)
and sends recent turns with each request; nothing is persisted server-side.
To keep long conversations from blowing up the token budget, we cap how much
raw history we send to the LLM and, for genuinely long conversations,
summarize the older portion on the fly for this one request only (the
summary is never stored — it's recomputed each time, which costs a bit more
than a persisted summary would, but avoids needing a database).
"""
from typing import List, Dict

from app.services.llm_provider import LLMProvider, LLMError

RECENT_TURNS_KEPT = 8    # last N raw turns sent verbatim
SUMMARIZE_AFTER = 16     # only summarize older turns once history exceeds this


def build_context_messages(history: List[Dict[str, str]], llm: LLMProvider = None) -> List[Dict[str, str]]:
    """history: list of {"role": "user"|"assistant", "content": str}, oldest first.
    Returns the message list to prepend before the new user turn."""
    if not history:
        return []

    recent = history[-RECENT_TURNS_KEPT:]
    older = history[:-RECENT_TURNS_KEPT] if len(history) > RECENT_TURNS_KEPT else []

    messages = []
    if older and len(history) > SUMMARIZE_AFTER and llm is not None:
        summary = _summarize(older, llm)
        if summary:
            messages.append({
                "role": "system",
                "content": f"Summary of earlier conversation with this farmer: {summary}",
            })

    messages.extend(recent)
    return messages


def _summarize(turns: List[Dict[str, str]], llm: LLMProvider) -> str:
    transcript = "\n".join(f"{t['role']}: {t['content']}" for t in turns)
    prompt = [
        {"role": "system", "content": (
            "Summarize this farmer's earlier conversation in 3-5 concise sentences, "
            "keeping any concrete facts (crop, location, soil values, decisions made). "
            "Write the summary in English regardless of the conversation's language."
        )},
        {"role": "user", "content": transcript},
    ]
    try:
        result = llm.chat(prompt, temperature=0.2, max_tokens=300)
        return result["content"]
    except LLMError:
        return ""  # non-critical — proceed without a summary rather than fail the request
