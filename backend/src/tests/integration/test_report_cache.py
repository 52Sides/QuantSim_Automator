import pytest
import fakeredis
from unittest.mock import patch
from pathlib import Path


@pytest.mark.integration
@pytest.mark.asyncio
async def test_report_cached_in_redis(async_client, tmp_path, mock_simulation_in_db):
    """
    Проверяет, что если отчёт уже есть в Redis — он возвращается сразу,
    без вызова Celery-задачи.
    """

    # --- создаём фейковый Redis и помещаем туда ссылку на готовый файл ---
    redis_client = fakeredis.FakeStrictRedis()
    fake_report_path = tmp_path / f"report_{mock_simulation_in_db.id}.xlsx"
    fake_report_path.write_text("fake binary data")
    redis_client.set(f"report:{mock_simulation_in_db.id}", str(fake_report_path))

    # --- подменяем реальный Redis внутри эндпоинта на наш mock ---
    with patch("api.routes.report.redis_client", redis_client):
        # Запросим отчёт
        resp = await async_client.get(f"/report/{mock_simulation_in_db.id}")
        assert resp.status_code == 200, "Если отчёт есть в Redis — должен быть 200 OK"

        content_type = resp.headers.get("content-type", "")
        assert "application/vnd.openxmlformats" in content_type, "Должен вернуться XLSX файл"

    # --- Проверим, что Celery не вызывался ---
    with patch("api.routes.report.generate_report_task.delay") as mocked_celery:
        _ = await async_client.get(f"/report/{mock_simulation_in_db.id}")
        mocked_celery.assert_not_called()
