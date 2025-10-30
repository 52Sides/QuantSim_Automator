from fastapi import APIRouter, HTTPException
from schemas.simulation import SimulationRequest, SimulationResponse, PortfolioPoint
from core import parse_command_safe, build_portfolio_series, PortfolioSimulator

router = APIRouter(prefix="/simulate", tags=["Simulation"])


@router.post("/", response_model=SimulationResponse)
def simulate_portfolio(request: SimulationRequest):
    try:
        # --- парсим команду ---
        weights, sides, start, end = parse_command_safe(request.command)
        portfolio_series = build_portfolio_series(weights, sides, start, end, budget=10_000)

        # --- вычисляем метрики только по портфелю ---
        simulator = PortfolioSimulator(portfolio_series)
        result = simulator.run()

        portfolio_points = [
            PortfolioPoint(date=idx.strftime("%Y-%m-%d"), portfolio_value=float(val))
            for idx, val in result.cumulative.items()
        ]

        return SimulationResponse(
            cagr=result.cagr,
            sharpe=result.sharpe,
            max_drawdown=result.max_drawdown,
            portfolio=portfolio_points
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
