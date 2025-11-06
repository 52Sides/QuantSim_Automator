from openpyxl import Workbook
from pathlib import Path

REPORTS_DIR = Path("/app/reports")
REPORTS_DIR.mkdir(exist_ok=True)

async def generate_xlsx_report(simulation):
    wb = Workbook()
    ws = wb.active
    ws.title = "Simulation Report"

    ws.append(["Simulation ID", simulation.id])
    ws.append(["Command", simulation.command])
    ws.append([])
    ws.append(["Metrics"])
    if simulation.metrics:
        ws.append(["CAGR", simulation.metrics.cagr])
        ws.append(["Sharpe", simulation.metrics.sharpe])
        ws.append(["Max Drawdown", simulation.metrics.max_drawdown])
    ws.append([])
    ws.append(["Date", "Portfolio Value"])
    for p in simulation.result_json:
        ws.append([p["date"], p["portfolio_value"]])

    path = REPORTS_DIR / f"{simulation.id}.xlsx"
    wb.save(path)
    return path
