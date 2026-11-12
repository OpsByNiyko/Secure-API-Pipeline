import logging
import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.config import get_settings

logger = logging.getLogger(__name__)


api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)


def verify_api_key(
    api_key: Annotated[str | None, Depends(api_key_header)],
) -> None:
    """Verify the supplied API key."""

    expected_key = get_settings().api_key.get_secret_value()

    if api_key is None or not secrets.compare_digest(
        api_key,
        expected_key,
    ):
        logger.warning("Rejected request due to invalid or missing API key")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
