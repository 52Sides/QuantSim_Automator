import pytest

@pytest.mark.integration
@pytest.mark.asyncio
async def test_metrics_endpoint(async_client):
    resp = await async_client.get("/metrics")
    assert resp.status_code == 200
    assert "http_requests_total" in resp.text

@pytest.mark.integration
@pytest.mark.asyncio
async def test_prometheus_status():
    import httpx
    async with httpx.AsyncClient() as client:
        resp = await client.get("http://localhost:9090/api/v1/status/config")
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
