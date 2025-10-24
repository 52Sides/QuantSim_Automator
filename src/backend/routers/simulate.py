from fastapi import APIRouter, HTTPException
from backend.schemas.simulation import SimulationRequest, SimulationResponse
from core.portfolio import PortfolioSimulator
from core.fetchers.yfinance_fetcher import fetch_price_series

router = APIRouter(prefix="/simulate", tags=["Simulation"])

@router.post("/", response_model=SimulationResponse)
def simulate_portfolio(request: SimulationRequest):
    try:
        prices = fetch_price_series(
            request.ticker,
            request.start.strftime("%Y-%m-%d"),
            request.end.strftime("%Y-%m-%d")
        )
        simulator = PortfolioSimulator(prices)
        metrics = simulator.calculate_metrics()

        return SimulationResponse(
            ticker=request.ticker,
            start=request.start,
            end=request.end,
            cagr=metrics["CAGR"],
            sharpe=metrics["Sharpe Ratio"],
            max_drawdown=metrics["Max Drawdown"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
