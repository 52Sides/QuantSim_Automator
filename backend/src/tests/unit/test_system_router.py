from fastapi.testclient import TestClient
from api.main import app


def test_system_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
