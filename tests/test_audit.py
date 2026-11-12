import app.main as main


def test_unexpected_error_returns_generic_response(
    client,
    test_settings,
    monkeypatch,
):
    """Unexpected exceptions should not expose internal details."""

    def raise_database_error(event_id):
        raise RuntimeError("Sensitive internal database failure")

    monkeypatch.setattr(
        main,
        "get_event_by_id",
        raise_database_error,
    )

    response = client.get(
        "/events/1",
        headers={"X-API-Key": test_settings.api_key.get_secret_value()},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}

    assert "Sensitive internal database failure" not in response.text


def test_create_audit_event(client, test_settings):
    """An authenticated user should be able to create an event."""

    api_key = test_settings.api_key.get_secret_value()

    payload = {
        "event_type": "user.login",
        "actor": "admin",
        "description": "Successful user authentication",
        "severity": "info",
    }

    response = client.post(
        "/events",
        json=payload,
        headers={"X-API-Key": api_key},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["event_type"] == "user.login"
    assert data["actor"] == "admin"
    assert data["severity"] == "info"
    assert "created_at" in data


def test_create_event_without_api_key_returns_401(client):
    """Requests without an API key should be rejected."""

    response = client.post(
        "/events",
        json={
            "event_type": "user.login",
            "actor": "admin",
            "description": "Authentication test",
            "severity": "info",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_create_event_with_invalid_api_key_returns_401(client):
    """Requests with an incorrect API key should be rejected."""

    response = client.post(
        "/events",
        headers={"X-API-Key": "incorrect-key"},
        json={
            "event_type": "user.login",
            "actor": "admin",
            "description": "Authentication test",
            "severity": "info",
        },
    )

    assert response.status_code == 401


def test_retrieve_events_without_api_key_returns_401(client):
    """Audit records must not be publicly accessible."""

    response = client.get("/events")

    assert response.status_code == 401


def test_invalid_severity_returns_422(client, test_settings):
    """Unsupported severity values should be rejected."""

    response = client.post(
        "/events",
        headers={"X-API-Key": test_settings.api_key.get_secret_value()},
        json={
            "event_type": "user.login",
            "actor": "admin",
            "description": "Invalid severity test",
            "severity": "superuser",
        },
    )

    assert response.status_code == 422


def test_unexpected_fields_are_rejected(client, test_settings):
    """Requests containing undefined fields should be rejected."""

    response = client.post(
        "/events",
        headers={"X-API-Key": test_settings.api_key.get_secret_value()},
        json={
            "event_type": "user.login",
            "actor": "admin",
            "description": "Unexpected field test",
            "severity": "info",
            "is_admin": True,
        },
    )

    assert response.status_code == 422


def test_invalid_event_type_returns_422(client, test_settings):
    """Event types must follow the defined naming convention."""

    response = client.post(
        "/events",
        headers={"X-API-Key": test_settings.api_key.get_secret_value()},
        json={
            "event_type": "INVALID EVENT!",
            "actor": "admin",
            "description": "Invalid event type test",
            "severity": "info",
        },
    )

    assert response.status_code == 422


def test_retrieve_audit_events(client, test_settings):
    """Created events should be available through the API."""

    api_key = test_settings.api_key.get_secret_value()
    headers = {"X-API-Key": api_key}

    payload = {
        "event_type": "user.login",
        "actor": "admin",
        "description": "Database retrieval test",
        "severity": "info",
    }

    create_response = client.post(
        "/events",
        json=payload,
        headers=headers,
    )

    assert create_response.status_code == 201

    response = client.get("/events", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["event_type"] == "user.login"


def test_retrieve_event_by_id(client, test_settings):
    """A specific event should be retrievable by its ID."""

    api_key = test_settings.api_key.get_secret_value()
    headers = {"X-API-Key": api_key}

    create_response = client.post(
        "/events",
        headers=headers,
        json={
            "event_type": "user.login",
            "actor": "admin",
            "description": "Individual event retrieval",
            "severity": "info",
        },
    )

    event_id = create_response.json()["id"]

    response = client.get(
        f"/events/{event_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == event_id


def test_retrieve_nonexistent_event_returns_404(client, test_settings):
    """Nonexistent event IDs should return HTTP 404."""

    response = client.get(
        "/events/99999",
        headers={"X-API-Key": test_settings.api_key.get_secret_value()},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Audit event not found"


def test_event_limit_accepts_valid_value(client, test_settings):
    """The event endpoint should accept valid limits."""

    response = client.get(
        "/events?limit=10",
        headers={"X-API-Key": test_settings.api_key.get_secret_value()},
    )

    assert response.status_code == 200


def test_event_limit_rejects_values_above_maximum(client, test_settings):
    """The event endpoint should reject limits above 100."""

    response = client.get(
        "/events?limit=101",
        headers={"X-API-Key": test_settings.api_key.get_secret_value()},
    )

    assert response.status_code == 422


def test_oversized_request_returns_413(client, test_settings):
    """Requests exceeding the body limit should be rejected."""

    response = client.post(
        "/events",
        headers={
            "X-API-Key": test_settings.api_key.get_secret_value(),
            "Content-Type": "application/json",
        },
        content="A" * 17_000,
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Request body too large"
