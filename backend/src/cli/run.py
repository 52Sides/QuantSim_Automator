import typer
import json
from datetime import datetime, timezone
from core import parse_command_safe, build_portfolio_series, PortfolioSimulator

app = typer.Typer(help="QuantSim Automator CLI")

@app.command()
def simulate(
    command: str = typer.Argument(..., help="Команда симуляции, например: 'TSLA-L-50% AAPL-S-50% 2020-01-01 2021-01-01'"),
):
    """Запуск симуляции портфеля по командной строке."""
    typer.echo(f"🔹 Симуляция портфеля: {command}")

    try:
        # --- парсим команду ---
        weights, sides, start, end = parse_command_safe(command)
        typer.echo(f"📈 Период: {start} → {end}")
        typer.echo(f"💼 Активы: {', '.join(weights.keys())}")

        # --- строим серию портфеля ---
        portfolio_series = build_portfolio_series(weights, sides, start, end, budget=10_000)

        # --- считаем метрики ---
        simulator = PortfolioSimulator(portfolio_series)
        result = simulator.run(meta={
            "command": command,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        typer.echo(f"\n✅ Результаты симуляции:")
        typer.echo(f"  CAGR: {result.cagr:.3%}")
        typer.echo(f"  Sharpe Ratio: {result.sharpe:.3f}")
        typer.echo(f"  Max Drawdown: {result.max_drawdown:.2%}")

        # --- сохраняем результат ---
        out = {
            "meta": result.meta,
            "cagr": result.cagr,
            "sharpe": result.sharpe,
            "max_drawdown": result.max_drawdown,
            "portfolio": [
                {"date": idx.strftime("%Y-%m-%d"), "portfolio_value": float(val)}
                for idx, val in result.cumulative.items()
            ],
        }
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        typer.echo("\n💾 Результаты сохранены в result.json")

    except Exception as e:
        typer.echo(f"❌ Ошибка: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
