import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from app.database import (
    create_event,
    get_event_by_id,
    get_events,
    init_db,
)
from app.middleware import (
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
)
from app.schemas.audit import AuditEventCreate, AuditEventResponse
from app.security import verify_api_key

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize application resources."""
    init_db()
    yield


app = FastAPI(
    title="Sentinel API",
    description="A secure audit event management API.",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    RequestSizeLimitMiddleware,
    max_body_size=16_384,
)

app.add_middleware(SecurityHeadersMiddleware)


@app.exception_handler(Exception)
async def handle_unexpected_error(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unexpected errors without exposing internal details."""

    logger.error(
        "Unhandled application error: %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    """Check application availability."""
    return {"status": "healthy"}


@app.post(
    "/events",
    response_model=AuditEventResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)],
)
def create_audit_event(event: AuditEventCreate):
    """Create a new audit event."""

    record = create_event(event)

    logger.info(
        "Audit event created: id=%s event_type=%s",
        record["id"],
        record["event_type"],
    )

    return record


@app.get(
    "/events",
    response_model=list[AuditEventResponse],
    dependencies=[Depends(verify_api_key)],
)
def list_audit_events(
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    """Retrieve audit events."""
    return get_events(limit)


@app.get(
    "/events/{event_id}",
    response_model=AuditEventResponse,
    dependencies=[Depends(verify_api_key)],
)
def retrieve_audit_event(event_id: int):
    """Retrieve an individual audit event."""

    event = get_event_by_id(event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit event not found",
        )

    return event
