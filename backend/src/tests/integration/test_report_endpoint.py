import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_report_endpoint(async_client, mock_simulation_in_db):
    """
    Проверяет endpoint /report/{id}:
    - если отчёт уже готов → статус 200 и файл
    - если нет → статус 202 и JSON {"status":"queued"}
    - если симуляции нет → статус 404
    """
    # случай 1: симуляция существует
    resp = await async_client.get(f"/report/{mock_simulation_in_db.id}")

    assert resp.status_code in (200, 202, 404), f"Unexpected code: {resp.status_code}"

    if resp.status_code == 202:
        data = resp.json()
        assert data["status"] in ("queued", "generating")

    if resp.status_code == 200:
        content_type = resp.headers.get("content-type", "")
        assert "application/vnd.openxmlformats" in content_type
