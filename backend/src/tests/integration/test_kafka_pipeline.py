import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_kafka_enqueue(async_client: AsyncClient):
    response = await async_client.post(
        "/simulate/kafka",
        json={"command": "AAPL-L-100% 2020-01-01 2020-12-31"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
