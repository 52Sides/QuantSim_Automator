import pytest
from celery.result import AsyncResult
from services.worker.tasks import run_simulation_task
from services.worker.celery_app import celery_app


@pytest.mark.integration
@pytest.mark.celery
def test_celery_simulation_task_executes_successfully():
    """Проверяем, что Celery-таск реально запускается и возвращает результат."""
    task = run_simulation_task.delay("AAPL-L-100% 2020-01-01 2020-12-31")
    result = AsyncResult(task.id, app=celery_app)
    result.get(timeout=30)

    assert result.successful(), f"Task failed: {result.result}"
    data = result.result
    assert isinstance(data, dict)
    assert data.get("status") in {"done", "SUCCESS"}
    assert "portfolio" in data["result"]
