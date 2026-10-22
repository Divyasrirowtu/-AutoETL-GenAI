from app.configuration import load_settings


def test_configuration_loads_successfully():
    settings = load_settings()

    assert settings["application"]["name"] == "AutoETL GenAI"
    assert settings["data"]["supported_formats"] == ["csv", "json"]
    assert settings["pipeline"]["max_retries"] == 3
    assert settings["pipeline"]["dry_run"] is True