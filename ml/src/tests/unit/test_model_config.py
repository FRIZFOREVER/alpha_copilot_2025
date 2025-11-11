from ml.configs.model_config import ModelSettings


def test_base_url_strips_whitespace() -> None:
    settings = ModelSettings.model_validate(
        {
            "base_url": " http://host ",
            "api_mode": "chat",
            "model": "dummy",
        }
    )

    assert settings.base_url == "http://host"
