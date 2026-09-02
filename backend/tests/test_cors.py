from app.main import app
from fastapi.testclient import TestClient


def test_cors_preflight_and_headers():
    client = TestClient(app)

    # Test OPTIONS preflight
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    }
    response = client.options("/api/v1/academic/attendance/241635", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") in ["*", "http://localhost:5173"]

    # Test GET with origin header
    resp = client.get("/health/live", headers={"Origin": "http://localhost:5173"})
    assert resp.status_code == 200
    assert "access-control-allow-origin" in resp.headers
