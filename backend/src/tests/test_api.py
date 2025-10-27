from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_simulate_endpoint():
    response = client.post("/simulate/", json={
        "ticker": "AAPL",
        "start": "2020-01-01",
        "end": "2020-06-01"
    })
    assert response.status_code == 200
    data = response.json()
    assert "cagr" in data
    assert "sharpe" in data
    assert "max_drawdown" in data
