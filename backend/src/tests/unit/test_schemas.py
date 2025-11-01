from schemas.simulation import SimulationRequest, SimulationResponse, PortfolioPoint


def test_schema_request_valid():
    req = SimulationRequest(command="TSLA-L-50% AAPL-S-50% 2020-01-01 2021-01-01")
    assert req.command.startswith("TSLA")


def test_schema_response_valid():
    p = PortfolioPoint(date="2020-01-01", portfolio_value=10000.0)
    res = SimulationResponse(cagr=0.12, sharpe=1.3, max_drawdown=0.1, portfolio=[p])
    assert res.cagr == 0.12
    assert isinstance(res.portfolio[0], PortfolioPoint)
