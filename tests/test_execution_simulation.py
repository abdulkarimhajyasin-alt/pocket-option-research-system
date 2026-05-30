"""Tests for Phase 20 execution simulation lab."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
import shutil

from fastapi.testclient import TestClient

from app.data.models import Candle, CandleSeries
from app.dashboard.routes import create_dashboard_app
from app.execution_simulator.analytics import SimulationAnalytics
from app.execution_simulator.engine import BinaryOutcomeEngine, ExecutionSimulator
from app.execution_simulator.models import (
    BinaryOutcome,
    ExpiryDuration,
    SimulatedOrder,
)
from app.execution_simulator.reports import ExecutionSimulationReporter
from app.safety.gates import SafetyGateConfig, SafetyGateService
from app.signals.signal import SignalDirection, TradeSignal


def make_candles() -> CandleSeries:
    base = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    candles = [
        Candle("EURUSD", "1m", base, 1.0000, 1.0020, 0.9990, 1.0000),
        Candle("EURUSD", "1m", base + timedelta(minutes=1), 1.0000, 1.0030, 0.9990, 1.0020),
        Candle("EURUSD", "1m", base + timedelta(minutes=2), 1.0020, 1.0025, 0.9980, 0.9990),
        Candle("EURUSD", "1m", base + timedelta(minutes=3), 0.9990, 1.0000, 0.9970, 0.9980),
        Candle("EURUSD", "1m", base + timedelta(minutes=4), 0.9980, 1.0010, 0.9970, 1.0000),
        Candle("EURUSD", "1m", base + timedelta(minutes=5), 1.0000, 1.0040, 0.9990, 1.0030),
    ]
    return CandleSeries("EURUSD", "1m", candles)


def make_signal(direction: SignalDirection, confidence: float = 0.7) -> TradeSignal:
    return TradeSignal(
        symbol="EURUSD",
        timeframe="1m",
        direction=direction,
        confidence=confidence,
        timestamp=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
        strategy_name="unit_strategy",
    )


def test_binary_outcome_engine_win_loss_and_draw() -> None:
    candles = make_candles()
    order = SimulatedOrder.create(
        "EURUSD",
        "1m",
        SignalDirection.CALL,
        0.7,
        candles[0].timestamp,
        "unit_strategy",
    )
    win = BinaryOutcomeEngine().evaluate(order, candles[0], candles[1])
    loss = BinaryOutcomeEngine().evaluate(order, candles[0], candles[2])
    draw = BinaryOutcomeEngine().evaluate(order, candles[0], candles[4])
    assert win.outcome == BinaryOutcome.WIN
    assert win.profit_loss == 0.8
    assert loss.outcome == BinaryOutcome.LOSS
    assert loss.profit_loss == -1.0
    assert draw.outcome == BinaryOutcome.DRAW
    assert draw.profit_loss == 0.0


def test_expiry_evaluation_uses_historical_future_candle() -> None:
    candles = make_candles()
    simulator = ExecutionSimulator(
        safety=SafetyGateService(),
        expiry=ExpiryDuration.MINUTES_3,
    )
    trade = simulator.simulate_signal(make_signal(SignalDirection.PUT), candles, 0)
    assert trade.expiry_time == candles[3].timestamp
    assert trade.outcome == BinaryOutcome.WIN


def test_safety_gate_rules_block_simulated_execution() -> None:
    low_confidence = SafetyGateService(SafetyGateConfig(minimum_confidence=0.8))
    assert low_confidence.evaluate_signal(make_signal(SignalDirection.CALL, 0.7)).reason == (
        "minimum_confidence"
    )
    max_trades = SafetyGateService(SafetyGateConfig(max_daily_trades=0))
    assert max_trades.evaluate_signal(make_signal(SignalDirection.CALL)).reason == (
        "max_daily_trades"
    )


def test_simulation_analytics_and_report_generation(tmp_path: Path) -> None:
    candles = make_candles()
    simulator = ExecutionSimulator(safety=SafetyGateService())
    trades = [
        simulator.simulate_signal(make_signal(SignalDirection.CALL), candles, 0),
        simulator.simulate_signal(make_signal(SignalDirection.PUT), candles, 1),
    ]
    analytics = SimulationAnalytics().summarize(trades)
    reports = ExecutionSimulationReporter(tmp_path).export(trades, analytics, "unit")
    assert analytics["total_trades"] == 2
    assert analytics["wins"] == 2
    assert analytics["win_rate"] == 1.0
    assert all(Path(path).exists() for path in reports.values())


def test_execution_dashboard_page_renders(tmp_path: Path) -> None:
    templates_src = Path(__file__).resolve().parents[1] / "app" / "templates"
    static_src = Path(__file__).resolve().parents[1] / "app" / "static"
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    shutil.copytree(templates_src, app_dir / "templates")
    shutil.copytree(static_src, app_dir / "static")

    client = TestClient(create_dashboard_app(tmp_path))
    response = client.get("/execution")
    assert response.status_code == 200
    assert "محاكاة التنفيذ" in response.text
    assert client.get("/api/execution").status_code == 200
