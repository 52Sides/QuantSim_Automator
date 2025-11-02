import pytest
from celery.result import AsyncResult
from services.worker.tasks import run_simulation_task
from services.worker.celery_app import celery_app


@pytest.mark.celery
def test_celery_simulation_task_executes_successfully():
    """Проверяем, что Celery-таск реально запускается и возвращает результат."""

    # Запускаем задачу
    task = run_simulation_task.delay("AAPL-L-100% 2020-01-01 2020-12-31")

    # Получаем результат через AsyncResult
    result = AsyncResult(task.id, app=celery_app)

    # Дожидаемся выполнения
    result.get(timeout=30)

    # Проверяем корректность ответа
    assert result.successful(), f"Task failed: {result.result}"
    data = result.result
    assert "status" in data and data["status"] == "SUCCESS"
    assert "cagr" in data
    assert "portfolio" in data
