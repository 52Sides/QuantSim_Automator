from fastapi import APIRouter, HTTPException
import pandas as pd

from backend.src.schemas.simulation import SimulationRequest, SimulationResponse
from backend.src.core.portfolio import PortfolioSimulator
from backend.src.core.fetchers.yfinance_fetcher import fetch_price_series


router = APIRouter(prefix="/simulate", tags=["Simulation"])

@router.post("/", response_model=SimulationResponse)
def simulate_portfolio(request: SimulationRequest):
    """
    Один API вызов: получает котировки Yahoo, считает метрики, возвращает результат и данные для графика.
    """
    try:
        # Загружаем котировки
        prices = fetch_price_series(
            request.ticker,
            request.start.strftime("%Y-%m-%d"),
            request.end.strftime("%Y-%m-%d")
        )

        if prices.empty:
            raise HTTPException(status_code=404, detail="No price data found for given period")

        # Считаем метрики
        simulator = PortfolioSimulator(prices)
        metrics = simulator.calculate_metrics()

        # Готовим данные для графика
        price_data = [
            {"date": d.strftime("%Y-%m-%d"), "close": float(p)}
            for d, p in prices.items()
        ]

        # Возвращаем всё сразу
        return {
            "ticker": request.ticker,
            "start": request.start,
            "end": request.end,
            "cagr": metrics["CAGR"],
            "sharpe": metrics["Sharpe Ratio"],
            "max_drawdown": metrics["Max Drawdown"],
            "prices": price_data
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
