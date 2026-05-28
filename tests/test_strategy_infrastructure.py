"""Tests for strategy infrastructure."""

from datetime import UTC, datetime, time

from app.config.strategy_config import StrategyConfigLoader
from app.data.timeframe_manager import TimeframeManager
from app.signals.confidence import ConfidenceScorer, WeightedScore
from app.signals.session_filter import SessionFilter, SessionWindow
from app.strategies.registry import default_strategy_registry


def test_strategy_registry_creates_strategy_from_config() -> None:
    config = StrategyConfigLoader().load("configs/strategies/sample_strategy.yaml")
    strategy = default_strategy_registry().create_from_config(config)

    assert strategy.name == "sample_candle_direction_strategy"
    assert strategy.parameters.symbols == ("EURUSD",)


def test_session_filter_accepts_configured_window() -> None:
    session_filter = SessionFilter(
        sessions={"custom": SessionWindow("custom", time(9, 0), time(10, 0))}
    )
    timestamp = datetime(2026, 1, 1, 9, 30, tzinfo=UTC)

    assert session_filter.is_allowed(timestamp, ("custom",)) is True


def test_confidence_scorer_weighted_threshold() -> None:
    scorer = ConfidenceScorer(threshold=0.6)
    confidence = scorer.weighted(
        [
            WeightedScore("trend", 0.8, 2.0),
            WeightedScore("pattern", 0.4, 1.0),
        ]
    )

    assert confidence == 0.6667
    assert scorer.passes(confidence) is True


def test_timeframe_manager_compares_timeframes() -> None:
    manager = TimeframeManager()

    assert manager.compare("1m", "5m") == -1
    assert "1h" in manager.higher_timeframes("5m")
