import typer
import json
from datetime import datetime

from core.fetchers.yfinance_fetcher import fetch_price_series
from core.portfolio import PortfolioSimulator

app = typer.Typer(help="QuantSim Automator — minimal CLI MVP")


@app.command()
def simulate(ticker: str = typer.Argument(..., help="Ticker symbol, e.g. AAPL"),
             start: str = "--start",
             end: str = "--end"):
    """
    Запустить простую локальную симуляцию для одного тикера.
    Пример: python -m cli.run simulate AAPL --start 2020-01-01 --end 2021-01-01
    """
    typer.echo(f"Fetching prices for {ticker} from {start} to {end}...")
    prices = fetch_price_series(ticker, start, end)
    sim = PortfolioSimulator(prices)
    result = sim.run(meta={"ticker": ticker, "start": start, "end": end, "timestamp": datetime.utcnow().isoformat()})
    # Вывод метрик
    typer.echo(f"CAGR: {result.cagr:.2%}")
    typer.echo(f"Sharpe: {result.sharpe:.4f}")
    typer.echo(f"Max drawdown: {result.max_drawdown:.2%}")
    # Сохранить результат в JSON (простая сериализация метрик)
    out = {
        "meta": result.meta,
        "cagr": result.cagr,
        "sharpe": result.sharpe,
        "max_drawdown": result.max_drawdown,
    }
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    typer.echo("Result saved to result.json")
