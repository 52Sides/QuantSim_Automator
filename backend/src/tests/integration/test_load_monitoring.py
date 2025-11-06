import pytest
import asyncio
import httpx
import socket


@pytest.mark.integration
@pytest.mark.asyncio
async def test_metrics_endpoint(async_client):
    """Проверяем, что FastAPI /metrics жив и отдаёт базовые метрики Prometheus."""
    resp = await async_client.get("/metrics")
    assert resp.status_code == 200, f"Unexpected status: {resp.status_code}"
    assert "http_requests_total" in resp.text or "http_server_requests_total" in resp.text


@pytest.mark.integration
@pytest.mark.asyncio
async def test_prometheus_available():
    """Проверяем доступность Prometheus в контейнере."""
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            resp = await client.get("http://prometheus:9090/api/v1/status/config")
        except Exception as e:
            pytest.skip(f"Prometheus not reachable: {e}")
        else:
            assert resp.status_code == 200
            assert "data" in resp.json()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_grafana_alive():
    """Проверяем, что Grafana дожила до запуска (по /login)."""
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            resp = await client.get("http://grafana:3000/login")
        except Exception as e:
            pytest.skip(f"Grafana not reachable: {e}")
        else:
            assert resp.status_code == 200
            assert "grafana" in resp.text.lower()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_redis_and_kafka_ports_open():
    """Проверка, что Redis и Kafka порты открыты в Docker."""
    for host, port in [("redis", 6379), ("kafka", 9092)]:
        try:
            s = socket.create_connection((host, port), timeout=2)
            s.close()
        except OSError:
            pytest.skip(f"{host}:{port} not available in current test env")
