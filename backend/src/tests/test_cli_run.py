import json
from typer.testing import CliRunner
from cli.run import app

runner = CliRunner()


def test_cli_simulate_success(monkeypatch, tmp_path):
    """Проверяем успешный запуск CLI"""

    import core
    import pandas as pd

    # --- фиктивные функции ---
    def fake_parse(cmd):
        return {"AAPL": 1.0}, {"AAPL": "L"}, "2020-01-01", "2020-06-01"

    def fake_build(weights, sides, start, end, budget):
        idx = pd.date_range(start, end, freq="ME")
        return pd.Series([100 + i for i in range(len(idx))], index=idx)

    class FakeSimulator:
        def __init__(self, series): ...

        def run(self, meta=None):
            import pandas as pd
            idx = pd.date_range("2020-01-01", "2020-06-01", freq="ME")
            returns = pd.Series([0.01] * (len(idx) - 1), index=idx[1:])
            cumulative = pd.Series([1.0 + i * 0.01 for i in range(len(idx))], index=idx)
            return core.SimulationResult(
                returns=returns,
                cumulative=cumulative,
                cagr=0.1, sharpe=1.2, max_drawdown=0.05,
                meta=meta or {}
            )

    # --- патчим CLI по реальному модулю ---
    monkeypatch.setattr("cli.run.parse_command_safe", fake_parse)
    monkeypatch.setattr("cli.run.build_portfolio_series", fake_build)
    monkeypatch.setattr("cli.run.PortfolioSimulator", FakeSimulator)

    # --- выполняем CLI из временной директории ---
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["AAPL-L-100% 2020-01-01 2020-06-01"])

    print(result.output)  # отладочный вывод, если что-то упадёт
    assert result.exit_code == 0, f"CLI crashed: {result.output}"
    assert "✅ Результаты симуляции" in result.output
    assert (tmp_path / "result.json").exists()


def test_cli_simulate_failure(monkeypatch):
    """Проверяем ошибку при неверной команде"""
    def fail_parse(_):
        raise ValueError("Invalid command")

    monkeypatch.setattr("cli.run.parse_command_safe", fail_parse)

    result = runner.invoke(app, ["AAPL-L-100% 2020-01-01 2020-06-01"])
    assert result.exit_code == 1
    assert "❌ Ошибка" in result.output
