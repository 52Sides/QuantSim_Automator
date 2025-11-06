import pytest
import asyncio
from pathlib import Path
from services.reports import generate_xlsx_report


@pytest.mark.unit
def test_generate_xlsx_report(tmp_path, mock_simulation):
    """
    Проверяет, что функция generate_xlsx_report создаёт корректный XLSX файл
    по данным симуляции.
    """
    # mock_simulation — фикстура, возвращающая объект с метриками и портфелем
    output_path: Path = asyncio.run(generate_xlsx_report(mock_simulation, tmp_path))
    assert output_path.exists(), "Файл отчёта должен существовать"
    assert output_path.suffix == ".xlsx", "Отчёт должен быть в формате XLSX"
    assert output_path.stat().st_size > 0, "Файл не должен быть пустым"
