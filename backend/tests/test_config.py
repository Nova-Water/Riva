from app.config import get_settings


def test_settings_load_with_defaults():
    settings = get_settings()
    assert settings.app_name == "RIVA AI"
    assert settings.backend_port == 8765
    assert settings.data_directory.exists()


def test_llm_not_configured_when_key_missing():
    settings = get_settings()
    settings.llm_api_key = ""
    settings.llm_model = ""
    assert settings.llm_configured() is False


def test_voice_not_configured_when_missing():
    settings = get_settings()
    settings.voice_api_key = ""
    settings.voice_id = ""
    assert settings.voice_configured() is False


def test_masked_hides_secret_value():
    settings = get_settings()
    masked = settings.masked("sk-1234567890abcdef")
    assert masked.startswith("sk-1")
    assert "1234567890abcdef" not in masked
