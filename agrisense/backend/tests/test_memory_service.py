import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services import memory_service


def test_build_context_messages_empty_history():
    assert memory_service.build_context_messages([]) == []
    assert memory_service.build_context_messages(None) == []


def test_build_context_messages_short_history_passthrough():
    history = [
        {"role": "user", "content": "I am growing wheat."},
        {"role": "assistant", "content": "Great, wheat is a rabi crop."},
    ]
    result = memory_service.build_context_messages(history)
    assert result == history  # short history: no summarization, sent verbatim


def test_build_context_messages_caps_long_history_without_llm():
    # 20 turns, no llm passed -> no summarization possible, but still capped
    # to the most recent RECENT_TURNS_KEPT turns rather than sending everything.
    history = [{"role": "user", "content": f"message {i}"} for i in range(20)]
    result = memory_service.build_context_messages(history, llm=None)
    assert len(result) == memory_service.RECENT_TURNS_KEPT
    assert result[-1]["content"] == "message 19"
