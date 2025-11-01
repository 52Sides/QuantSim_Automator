import importlib


def test_settings_loads_with_defaults(monkeypatch):
    env_vars = {
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "postgres",
        "POSTGRES_DB": "test_db",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "REDIS_URL": "redis://localhost:6379/0",
        "KAFKA_BROKER": "kafka:9092",
        "APP_ENV": "test",
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    import core.config as config
    importlib.reload(config)

    settings = config.Settings()

    assert settings.postgres_user == "postgres"
    assert settings.app_env == "test"
    assert isinstance(settings.postgres_port, int)
