import pytest
from pydantic import SecretStr, ValidationError

from app.config import Settings


def test_weak_api_key_is_rejected():
    """Configuration should reject API keys shorter than 32 characters."""

    with pytest.raises(ValidationError):
        Settings(
            api_key=SecretStr("short"),
            database_path="test.db",
        )


def test_valid_api_key_is_accepted():
    """Configuration should accept sufficiently long API keys."""

    settings = Settings(
        api_key=SecretStr("a" * 32),
        database_path="test.db",
    )

    assert len(settings.api_key.get_secret_value()) == 32
