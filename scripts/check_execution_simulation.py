"""Diagnostics for the offline execution simulation layer."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.data.models import Candle  # noqa: E402
from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.execution_simulator.engine import BinaryOutcomeEngine  # noqa: E402
from app.execution_simulator.lab import ExecutionSimulationLab  # noqa: E402
from app.execution_simulator.models import BinaryOutcome, SimulatedOrder  # noqa: E402
from app.safety.gates import SafetyGateConfig, SafetyGateService  # noqa: E402
from app.signals.signal import SignalDirection, TradeSignal  # noqa: E402


def main() -> None:
    """Run deterministic simulation diagnostics."""
    now = datetime(2026, 1, 1, tzinfo=UTC)
    entry = Candle("EURUSD", "1m", now, 1.0, 1.1, 0.9, 1.0)
    expiry = Candle("EURUSD", "1m", now + timedelta(minutes=1), 1.0, 1.2, 0.9, 1.1)
    order = SimulatedOrder.create(
        symbol="EURUSD",
        timeframe="1m",
        direction=SignalDirection.CALL,
        confidence=0.7,
        requested_at=now,
        strategy_name="diagnostic_strategy",
    )
    trade = BinaryOutcomeEngine().evaluate(order, entry, expiry)
    safety = SafetyGateService(SafetyGateConfig(max_daily_trades=0))
    signal = TradeSignal("EURUSD", "1m", SignalDirection.CALL, 0.7, now, "diagnostic")
    blocked = safety.evaluate_signal(signal)
    result = ExecutionSimulationLab(PROJECT_ROOT).run("diagnostic_execution_simulation")
    client = TestClient(create_dashboard_app(PROJECT_ROOT))
    page = client.get("/execution")
    checks = {
        "simulator_loads": trade.outcome == BinaryOutcome.WIN,
        "safety_gates": not blocked.approved and blocked.reason == "max_daily_trades",
        "reports_generate": all(Path(path).exists() for path in result.reports.values()),
        "dashboard_page": page.status_code == 200 and "محاكاة التنفيذ" in page.text,
        "api_page": client.get("/api/execution").status_code == 200,
        "local_only": bool(result.readiness),
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
