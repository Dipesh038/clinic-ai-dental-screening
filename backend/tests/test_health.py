from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_200_ok():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert isinstance(body["grad_cam_enabled"], bool)
