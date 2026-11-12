def test_health_endpoint_returns_200(client):
    """Health endpoint should return HTTP 200."""

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_health_endpoint_includes_security_headers(client):
    """HTTP responses should contain required security headers."""

    response = client.get("/health")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"

    assert (
        response.headers["permissions-policy"]
        == "camera=(), microphone=(), geolocation=()"
    )

    assert response.headers["cache-control"] == "no-store"
