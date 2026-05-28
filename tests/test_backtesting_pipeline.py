"""Tests for market data loading and backtesting pipeline behavior."""

from pathlib import Path

from app.backtesting.backtest_engine import BacktestEngine
from app.data.csv_loader import CsvCandleLoader
from app.risk.risk_engine import RiskEngine
from app.strategies.sample_strategy import SampleCandleDirectionStrategy


def test_csv_loader_loads_sample_dataset() -> None:
    """The sample dataset should load into a normalized candle series."""
    series = CsvCandleLoader().load(Path("data/sample_eurusd_m1.csv"), "EURUSD", "M1")

    assert len(series) == 200
    assert series.symbol == "EURUSD"
    assert series.timeframe == "1m"
    assert series.first is not None
    assert series.last is not None
    assert series.first.timestamp < series.last.timestamp


def test_backtest_engine_runs_sample_strategy() -> None:
    """The backtest engine should replay candles through BaseStrategy."""
    series = CsvCandleLoader().load(Path("data/sample_eurusd_m1.csv"), "EURUSD", "1m")
    engine = BacktestEngine(risk_engine=RiskEngine(min_confidence=0.6))
    result = engine.run(SampleCandleDirectionStrategy(), series)

    assert result.metrics["total_trades"] > 0
    assert result.metrics["wins"] + result.metrics["losses"] == result.metrics["total_trades"]
    assert len(result.equity_curve) == len(result.trades)
