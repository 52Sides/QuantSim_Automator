import typer
import json
from datetime import datetime
from backend.src.core import fetch_price_series
from backend.src.core import PortfolioSimulator

app = typer.Typer(help="QuantSim Automator CLI")

@app.command()
def simulate(
    ticker: str = typer.Argument(..., help="Ticker symbol, e.g. AAPL"),
    start: str = typer.Option(..., "--start", help="Start date YYYY-MM-DD"),
    end: str = typer.Option(..., "--end", help="End date YYYY-MM-DD"),
):
    """Запуск симуляции портфеля по одному тикеру."""
    typer.echo(f"Fetching prices for {ticker} from {start} to {end}...")
    prices = fetch_price_series(ticker, start, end)
    sim = PortfolioSimulator(prices)
    result = sim.run(meta={"ticker": ticker, "start": start, "end": end, "timestamp": datetime.utcnow().isoformat()})
    typer.echo(f"CAGR: {result.cagr:.2%}")
    typer.echo(f"Sharpe: {result.sharpe:.4f}")
    typer.echo(f"Max drawdown: {result.max_drawdown:.2%}")

    out = {
        "meta": result.meta,
        "cagr": result.cagr,
        "sharpe": result.sharpe,
        "max_drawdown": result.max_drawdown,
    }
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    typer.echo("Result saved to result.json")

if __name__ == "__main__":
    app()
