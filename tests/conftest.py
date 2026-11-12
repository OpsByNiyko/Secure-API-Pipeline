import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

import app.database as database
import app.security as security
from app.config import Settings
from app.main import app

TEST_API_KEY = "test-api-key-" + "x" * 32


@pytest.fixture
def test_settings(tmp_path):
    """Provide isolated settings for each test."""

    return Settings(
        api_key=SecretStr(TEST_API_KEY),
        database_path=str(tmp_path / "sentinel-test.db"),
    )


@pytest.fixture
def client(monkeypatch, test_settings):
    """Provide a test client with isolated dependencies."""

    monkeypatch.setattr(
        database,
        "get_settings",
        lambda: test_settings,
    )

    monkeypatch.setattr(
        security,
        "get_settings",
        lambda: test_settings,
    )

    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
