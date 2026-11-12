from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AuditEventCreate(BaseModel):
    """Schema for creating an audit event."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    event_type: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-z][a-z0-9_.-]*$",
    )
    actor: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=5, max_length=500)
    severity: Severity = Severity.INFO


class AuditEventResponse(BaseModel):
    """Schema returned when an audit event is retrieved."""

    id: int
    event_type: str
    actor: str
    description: str
    severity: Severity
    created_at: str
