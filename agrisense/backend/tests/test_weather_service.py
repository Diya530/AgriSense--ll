import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock
import requests

from app.services import weather_service


def test_fetch_openweathermap_raises_clear_error_without_key(monkeypatch):
    from app.config import get_settings
    get_settings.cache_clear()
    monkeypatch.setenv("OPENWEATHERMAP_API_KEY", "")
    monkeypatch.setenv("WEATHER_PROVIDER", "openweathermap")
    get_settings.cache_clear()

    try:
        weather_service._fetch_openweathermap(28.6, 77.2, 3)
        assert False, "Expected WeatherError"
    except weather_service.WeatherError as e:
        assert "OPENWEATHERMAP_API_KEY" in str(e)
    finally:
        get_settings.cache_clear()


@patch("app.services.weather_service.requests.get")
def test_fetch_openweathermap_handles_timeout(mock_get, monkeypatch):
    from app.config import get_settings
    monkeypatch.setenv("OPENWEATHERMAP_API_KEY", "fake-key-for-test")
    get_settings.cache_clear()

    mock_get.side_effect = requests.Timeout("simulated timeout")

    try:
        weather_service._fetch_openweathermap(28.6, 77.2, 3)
        assert False, "Expected WeatherError on timeout"
    except weather_service.WeatherError as e:
        assert "timed out" in str(e).lower()
    finally:
        get_settings.cache_clear()


@patch("app.services.weather_service.requests.get")
def test_fetch_openweathermap_handles_invalid_key(mock_get, monkeypatch):
    from app.config import get_settings
    monkeypatch.setenv("OPENWEATHERMAP_API_KEY", "fake-key-for-test")
    get_settings.cache_clear()

    resp = MagicMock()
    resp.raise_for_status.side_effect = requests.HTTPError(response=MagicMock(status_code=401))
    mock_get.return_value = resp

    try:
        weather_service._fetch_openweathermap(28.6, 77.2, 3)
        assert False, "Expected WeatherError on 401"
    except weather_service.WeatherError as e:
        assert "invalid" in str(e).lower() or "key" in str(e).lower()
    finally:
        get_settings.cache_clear()


def test_wmo_code_mapping_unknown_code_is_honest():
    assert weather_service._wmo_code_to_text(9999) == "Unknown"
    assert weather_service._wmo_code_to_text(None) == "Unknown"
