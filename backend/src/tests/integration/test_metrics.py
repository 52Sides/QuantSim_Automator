import pytest
import httpx

@pytest.mark.integration
@pytest.mark.asyncio
async def test_metrics_endpoint_available(async_client: httpx.AsyncClient):
    resp = await async_client.get("/metrics")
    assert resp.status_code == 200
    assert "http_request_duration_seconds" in resp.text
