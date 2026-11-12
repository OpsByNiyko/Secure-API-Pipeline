import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from app.config import get_settings
from app.schemas.audit import AuditEventCreate


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Create and safely manage a database connection."""

    database_path = Path(get_settings().database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db() -> None:
    """Initialize the audit events table."""

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                actor TEXT NOT NULL,
                description TEXT NOT NULL,
                severity TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def create_event(event: AuditEventCreate) -> dict:
    """Insert an audit event and return the stored record."""

    created_at = datetime.now(UTC).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO audit_events (
                event_type,
                actor,
                description,
                severity,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                event.event_type,
                event.actor,
                event.description,
                event.severity.value,
                created_at,
            ),
        )

        event_id = cursor.lastrowid

        row = connection.execute(
            "SELECT * FROM audit_events WHERE id = ?",
            (event_id,),
        ).fetchone()

        return dict(row)


def get_events(limit: int = 100) -> list[dict]:
    """Retrieve the most recent audit events."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM audit_events
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [dict(row) for row in rows]


def get_event_by_id(event_id: int) -> dict | None:
    """Retrieve a specific audit event."""

    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM audit_events WHERE id = ?",
            (event_id,),
        ).fetchone()

        return dict(row) if row else None
